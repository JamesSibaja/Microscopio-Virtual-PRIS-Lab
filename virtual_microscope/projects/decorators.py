
from functools import wraps
from django.http import HttpResponseForbidden
from projects.models import Project


def project_collaborator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, project_id, *args, **kwargs):
        # Verificar si el usuario actual es un colaborador del proyecto
        if user_is_project_collaborator(request.user, project_id):
            return view_func(request, project_id, *args, **kwargs)
        else:
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return _wrapped_view

def user_is_project_collaborator(user, project):
    try:
        projectCheck = Project.objects.get(id=project)

        return user in projectCheck.adminUsers.all() or user in projectCheck.sharedUsers.all() or user == projectCheck.user
    
    except:
        return False