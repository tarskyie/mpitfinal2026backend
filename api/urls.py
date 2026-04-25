from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, TaskViewSet, SolutionViewSet, ParentTaskViewSet, ParentStudentDetailView

router = DefaultRouter()
# urls.py
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'tasks', TaskViewSet)
router.register(r'solutions', SolutionViewSet, basename='solution')
router.register(r'parent-tasks', ParentTaskViewSet, basename='parent-tasks')
router.register(r'parent-student-detail', ParentStudentDetailView, basename='parent-student-detail')

urlpatterns = [
    path('', include(router.urls)),
]
