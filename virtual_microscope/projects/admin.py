from django.contrib import admin
from .models import Project, Notes, ProjectSlide,Message
from .forms import ProjectAdmin

# Register your models here.
admin.site.register(Project,ProjectAdmin)
admin.site.register(Notes)
admin.site.register(ProjectSlide)
admin.site.register(Message)