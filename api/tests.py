from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Group, Task, Solution, ParentStudent

class RemoteEducationAPITests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='password', user_type='teacher')
        self.student = User.objects.create_user(username='student', password='password', user_type='student')
        self.parent = User.objects.create_user(username='parent', password='password', user_type='parent')

        ParentStudent.objects.create(parent=self.parent, student=self.student)

        self.group = Group.objects.create(name='Test Group', teacher=self.teacher)
        self.group.students.add(self.student)

        self.task = Task.objects.create(
            title='Test Task',
            group=self.group,
            expiration_date=timezone.now() + timedelta(days=1),
            created_by=self.teacher
        )

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 3)

    def test_group_creation(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('group-list')
        data = {'name': 'New Group'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2)

    def test_student_join_group(self):
        new_student = User.objects.create_user(username='new_student', password='password', user_type='student')
        self.client.force_authenticate(user=new_student)
        url = reverse('group-join', kwargs={'pk': self.group.pk})
        data = {'invite_code': self.group.invite_code}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(new_student, self.group.students.all())

    def test_task_creation(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('task-list')
        data = {
            'title': 'New Task',
            'group': self.group.pk,
            'expiration_date': timezone.now() + timedelta(days=2)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_solution_submission(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('solution-list')
        data = {
            'task': self.task.pk,
            'text': 'This is my solution.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Solution.objects.count(), 1)

    def test_solution_submission_expired(self):
        self.task.expiration_date = timezone.now() - timedelta(days=1)
        self.task.save()
        self.client.force_authenticate(user=self.student)
        url = reverse('solution-list')
        data = {
            'task': self.task.pk,
            'text': 'This is my solution.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_parent_task_view(self):
        self.client.force_authenticate(user=self.parent)
        url = reverse('parent-tasks-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Task')
