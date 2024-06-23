import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_microscope.settings')
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class OpenSlide(models.Model):
    name = models.CharField(unique=True, max_length=50)
    path = models.CharField(max_length=50,null=True)
    # file = models.FileField(max_length=50,null=True)
    assembled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('open-micro-slide', args=[str(self.id)])

class ProcessingHistory(models.Model):
    # Referencia al usuario que realizó el procesamiento
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raw_slide = models.ForeignKey(OpenSlide, on_delete=models.SET_NULL,null=True, blank=True)
    # Nombre del archivo procesado
    file_name = models.CharField(max_length=255)
    
    # Estado del procesamiento
    STATUS_CHOICES = [
        ('SUCCESS', 'Éxito'),
        ('FAILURE', 'Fallo'),
    ]
    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    
    # Fecha y hora de inicio del procesamiento
    start_time = models.DateTimeField(auto_now_add=True)
    
    # Fecha y hora de finalización del procesamiento
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Duración del procesamiento (en segundos)
    duration = models.DurationField(null=True, blank=True)
    
    # Mensaje de error (si el procesamiento falló)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.file_name} - {self.status} - {self.start_time}"

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        super(ProcessingHistory, self).save(*args, **kwargs)

class Slide(models.Model):
    name = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=500)
    assembled = models.BooleanField(default=False)
    rawSlide = models.ForeignKey(OpenSlide, on_delete=models.CASCADE, null=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    zoomI = models.IntegerField(null=True)
    zoomM = models.IntegerField(null=True)
    zoomMin = models.IntegerField(null=True)
    path = models.CharField(max_length=50,null=True)
    image = models.ImageField(upload_to='slides',null=True,)
    # centerLat = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    # centerLng = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    maxLatLng = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    factor = models.DecimalField(max_digits=10, decimal_places=8, null=True)
    error = models.BooleanField(default=False,null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('micro-slide', args=[str(self.id)])

    def getAbsoluteUrl(self):
        return reverse('micro-slide-full', args=[str(self.id)])

