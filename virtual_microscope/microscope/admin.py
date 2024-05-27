from django.contrib import admin
from .models import Slide,OpenSlide,ProcessingHistory

# Register your models here.
# class SlideAdmin(admin.ModelAdmin):
    

admin.site.register(Slide)
admin.site.register(OpenSlide)
class ProcessingHistoryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'status', 'start_time', 'end_time', 'duration', 'user')
    list_filter = ('status', 'start_time', 'user')
admin.site.register(ProcessingHistory, ProcessingHistoryAdmin)