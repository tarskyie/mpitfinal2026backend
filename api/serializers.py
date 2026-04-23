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

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'group', 'expiration_date', 'created_by')
        read_only_fields = ('created_by',)

class ParentTaskSerializer(serializers.ModelSerializer):
    status = serializers.CharField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'group', 'expiration_date', 'created_by', 'status')
        read_only_fields = ('created_by',)


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ('id', 'task', 'student', 'text', 'grade', 'submitted_at')
        read_only_fields = ('student', 'submitted_at')

class ParentStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentStudent
        fields = ('id', 'parent', 'student')
