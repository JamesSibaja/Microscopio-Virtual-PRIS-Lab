from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from projects.views import *

urlpatterns = [
    path('project/',login_required(projects.as_view()),name='project-list'),
    path('project2/<int:slideId>',login_required(projects.as_view()),name='project-list-dos'),
    path('projectDetail/<int:pk>/<int:option>/<int:map>',login_required(projectDetail.as_view()),name='project-detail'),
    path('projectProfileDetail/<int:pk>/<int:option>/<int:map>',login_required(projectProfileDetail.as_view()),name='project-profile-detail'),
    path('projectSlideDetail/<int:pk>/',login_required(projectSlideDetail.as_view()),name='project-slide-detail'),
    path('noteDetail/<int:pk>/<int:project_id>',login_required(noteDetail.as_view()),name='note-detail'),
    path('deleteNota/<int:nota_id>', deleteNota),
    path('deleteProject/<int:project_id>', deleteProject),
    path('deleteProjectSlide/<int:slide_id>', login_required(deleteProjectSlide)),
    path('showNote/<int:note_id>/<int:project_id>', showNote),
    path('newProjectUser/<int:project_id>/<int:projectUser_id>', newProjectUser),
    path('deleteProjectUser/<int:project_id>/<int:projectUser_id>', deleteProjectUser),
    path('newProjectInvitedUser/<int:project_id>/<int:projectUser_id>', newProjectInvitedUser),
    path('deleteProjectInvitedUser/<int:project_id>/<int:projectUser_id>', deleteProjectInvitedUser),
    path('obtener_lista/', obtener_lista, name='obtener_lista'),
    path('datos_actualizados_catalogo/<int:project>/<str:buscar>', datos_actualizados_catalogo, name='datos_actualizados_catalogo'),
    path('datos_actualizados_placas/<int:project>/<str:buscar>', datos_actualizados_placas, name='datos_actualizados_placas'),
    path('datos_actualizados_colaboradores/<int:project>/<str:buscar>', datos_actualizados_colaboradores, name='datos_actualizados_colaboradores'),
    path('datos_actualizados_chat/<int:project>/<str:buscar>', datos_actualizados_chat, name='datos_actualizados_chat'),
]
