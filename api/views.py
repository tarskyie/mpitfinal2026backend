from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Group, Task, Solution, ParentStudent, User
from .serializers import GroupSerializer, TaskSerializer, SolutionSerializer, ParentTaskSerializer, SolutionGradeUpdateSerializer, SolutionCreateSerializer, StudentSerializer
from .permissions import IsTeacher, IsStudent, IsParent, IsTeacherOfSolutionGroup

from rest_framework.views import APIView
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import openai

class PreviewGradesView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        if task.group.teacher != request.user:
            return Response({"error": "You are not the teacher of this group"}, status=status.HTTP_403_FORBIDDEN)

        solutions = Solution.objects.filter(task=task)
        if not solutions.exists():
            return Response({"message": "No solutions submitted for this task yet."}, status=status.HTTP_200_OK)

        client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_URL,
        )

        results = []
        for solution in solutions:
            prompt = f"Task: {task.title}\n\nDescription: {task.description}\n\nStudent's solution:\n{solution.text}\n\n---\n\nGrade the solution on a scale of 1 to 10."
            
            try:
                completion = client.chat.completions.create(
                    model=settings.OPENAI_API_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that grades student solutions."},
                        {"role": "user", "content": prompt},
                    ],
                )
                
                preview_grade = completion.choices[0].message.content.strip()
                results.append({
                    "solution_id": solution.id,
                    "student_id": solution.student.id,
                    "student_name": solution.student.username,
                    "preview_grade": preview_grade
                })

            except Exception as e:
                return Response({"error": f"An error occurred with the AI service: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(results, status=status.HTTP_200_OK)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
    def get_permissions(self):
        # Only teachers can create groups
        if self.action == 'create':
            return [IsTeacher()]
        
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'join':
            return GroupJoinSerializer 
        return GroupSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        is_teacher = instance.teacher == request.user
        is_student = instance.students.filter(id=request.user.id).exists()
        
        if not (is_teacher or is_student):
            return Response(
                {"detail": "You do not have permission to view this group's full info."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsStudent])
    def join(self, request, pk=None):
        group = self.get_object() 
        invite_code = request.data.get('invite_code')
        
        if group.invite_code == invite_code:
            group.students.add(request.user)
            return Response({'status': 'Joined successfully'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid invite code'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsTeacher]
        return super().get_permissions()

class SolutionViewSet(viewsets.ModelViewSet):
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SolutionCreateSerializer
        if self.action in ['update', 'partial_update']:
            return SolutionGradeUpdateSerializer
        return SolutionSerializer

    def perform_create(self, serializer):
        task = serializer.validated_data['task']
        if task.expiration_date < timezone.now():
            raise serializers.ValidationError("Task has expired")
        serializer.save(student=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsStudent]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsTeacherOfSolutionGroup]
        return super().get_permissions()

class ParentTaskViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ParentTaskSerializer
    permission_classes = [IsParent]

    def get_queryset(self):
        try:
            parent_student = ParentStudent.objects.get(parent=self.request.user)
            student = parent_student.student
            tasks = Task.objects.filter(group__students=student)
            
            for task in tasks:
                solution = Solution.objects.filter(task=task, student=student).first()
                if solution:
                    if solution.grade:
                        task.status = solution.grade
                    else:
                        task.status = "not done"
                elif task.expiration_date < timezone.now():
                    task.status = "expired"
                else:
                    task.status = "not done"
            return tasks
        except ParentStudent.DoesNotExist:
            return Task.objects.none()

class ParentStudentDetailView(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsParent]

    def get_queryset(self):
        try:
            parent_student = ParentStudent.objects.get(parent=self.request.user)
            student = parent_student.student
            return User.objects.filter(id=student.id)
        except ParentStudent.DoesNotExist:
            return User.objects.none()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"detail": "No student linked to this parent."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)
