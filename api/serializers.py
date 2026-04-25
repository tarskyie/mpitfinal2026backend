from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from .models import User, Group, Task, Solution, ParentStudent

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'user_type')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'teacher', 'students', 'invite_code')
        read_only_fields = ('teacher', 'invite_code')

class GroupJoinSerializer(serializers.ModelSerializer):
    """
    Serializer used specifically for the 'join' action.
    Hides sensitive data while providing basic identification.
    """
    # We use a ReadOnlyField to show the teacher's name without exposing the User ID or full object
    teacher_name = serializers.ReadOnlyField(source='teacher.get_full_name')

    class Meta:
        model = Group
        # Only expose non-sensitive identifying information
        fields = ['id', 'name', 'teacher_name']
        read_only_fields = ['id', 'name', 'teacher_name']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'group', 'expiration_date', 'created_by')
        read_only_fields = ('created_by',)

class ParentTaskSerializer(serializers.ModelSerializer):
    status = serializers.CharField()
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'group', 'expiration_date', 'created_by', 'status', 'group_name')
        read_only_fields = ('created_by',)


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('id', 'task', 'student', 'text', 'grade', 'submitted_at')
        read_only_fields = ('student', 'submitted_at', 'task', 'text')

class SolutionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('task', 'text')

class SolutionGradeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('grade',)

class ParentStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentStudent
        fields = ('id', 'parent', 'student')

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')
