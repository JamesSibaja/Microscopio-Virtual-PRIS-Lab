import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_microscope.settings')
from microscope.models import Slide

from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from jsonfield import JSONField
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=25)
    description = models.CharField(max_length=500)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    adminUsers = models.ManyToManyField(User, related_name='adminUsers')
    sharedUsers = models.ManyToManyField(User, related_name='sharedUsers')
    invitedUsers = models.ManyToManyField(User, related_name='invitedUsers')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project-detail', args=[str(self.id),str(0),str(0)])

class ProjectSlide(models.Model):
    name = models.CharField(max_length=25)
    description = models.CharField(max_length=500)
    adminPermission = models.BooleanField(default=False)


    slide = models.ForeignKey(Slide, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('project-slide-detail', args=[str(self.id)])
    

class Notes(models.Model):
    name = models.CharField(max_length=50)
    
    description = models.TextField(max_length=500)
    geojson_data = models.TextField(null=True, blank=True)
    show = models.BooleanField()

    xUnoPos = models.FloatField()
    yUnoPos = models.FloatField()
    xDosPos = models.FloatField()
    yDosPos = models.FloatField()
    
    project = models.ForeignKey(ProjectSlide, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name  

    def get_absolute_url(self):
        return reverse('note-detail', args=[str(self.id),str(self.project.id)])
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project,  on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.contenido}"
    
