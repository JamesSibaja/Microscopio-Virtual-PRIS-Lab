from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from microscope.views import catalogo, micro, delete, deleteSlide, catalogo_edit, upload_view, activity_log
from . import views
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .views import historial_detalles

# from django_transfer import TransferHttpResponse

def admin_required(view_func):
    """
    Decorador que restringe el acceso a administradores.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Acceso denegado. Debes ser administrador para acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view



urlpatterns = [
    path('catalogo/', catalogo, name = "Catalogo"),
    path('catalogo_edit/<int:delete_edit>/', admin_required(catalogo_edit), name = "Catalogo_edit"),
    path('micro/<pk>/',micro.as_view(),name='micro-slide'),
    path('upload_file/', admin_required(views.upload_file), name='upload_file'),
    path('processing/', admin_required(views.processing), name='processing'),
    path('activity_log/', admin_required(views.activity_log), name='activity_log'),
    path('deleteSlide/<int:slide_id>', admin_required(deleteSlide)),
    path('delete/<int:slide_id>', admin_required(delete)),
    path('upload/', upload_view, name='upload'),
     path('task_status/<str:task_id>/', views.task_status, name='task_status'),
    path('historial/detalles/<int:id>/', historial_detalles, name='historial_detalles'),
    path('get/slide/data/<int:slide_id>/', views.get_slide_data, name='get_slide_data'),
]
