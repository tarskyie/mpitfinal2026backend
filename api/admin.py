from django.contrib import admin
from .models import User, Group, Task, Solution, ParentStudent

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Task)
admin.site.register(Solution)
admin.site.register(ParentStudent)
