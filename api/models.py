from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

def generate_invite_code():
    return uuid.uuid4().hex[:6].upper()

class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_groups')
    students = models.ManyToManyField(User, related_name='student_groups', blank=True)
    invite_code = models.CharField(max_length=10, unique=True, default=generate_invite_code)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=255)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='tasks')
    expiration_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')

    def __str__(self):
        return self.title

class Solution(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='solutions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solutions')
    text = models.TextField()
    grade = models.IntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'student')

class ParentStudent(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children_relations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_relations')

    class Meta:
        unique_together = ('parent', 'student')
