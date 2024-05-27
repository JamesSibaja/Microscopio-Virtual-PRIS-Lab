from django.shortcuts import get_object_or_404,render, redirect              
from django.views.generic import CreateView
from django.views import generic
from django.template import Template, context
from django.views.generic.edit import FormView, DeleteView
from django.db.models import Q
from projects.forms import NoteForm, ProjectForm, SearchForm, ProjectSlideForm, MensajeForm
from projects.models import Project, Notes, ProjectSlide, Message
from microscope.models import Slide
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.decorators import method_decorator
from .decorators import user_is_project_collaborator 
from django.http import HttpResponse


HttpResponse

class projects(generic.ListView,FormView,):
    template_name = "projects/projectList.html"
    model = Project
    form_class = ProjectForm
    paginate_by = 12
    
    def get_queryset(self):
        queryset2 = self.request.GET.get('buscar')
        usuario = self.request.user
        consulta = Q(user=usuario) | Q(sharedUsers=usuario)
        queryset = Project.objects.filter(consulta).distinct()
        if queryset2:
        
            palabras = queryset2.split()
            condiciones_busqueda = []

            for palabra in palabras:
                condicion = Q(name__icontains=palabra)
                condicion2 = Q(description__icontains=palabra) 
                condiciones_busqueda.append(condicion)
                condiciones_busqueda.append(condicion2)

            consulta = Q()
            for condicion in condiciones_busqueda:
                consulta |= condicion
            queryset = queryset.filter(consulta)

        return queryset



    def get_success_url(self):
        return self.request.path

    def get_context_data(self,**kwargs):
        context = super(projects, self).get_context_data(**kwargs)
        context['form'] = ProjectForm
        context['slideSel'] = None
        context['invite']= Project.objects.filter(invitedUsers=self.request.user)
        if self.request.path != '/project/':
            object_instance = Slide.objects.filter(id=self.kwargs['slideId'])
            for slide in object_instance:
                context['slideSel'] = slide
                context['make'] = True
        return context

    def post(self, request, *args, **kwargs):
        object_instance = request.user
        form = ProjectForm(request.POST)
        # print('jos')
        if form.is_valid():
            # mySlides = Slide.objects.filter(name=request.POST.get('slide', ''))
            print(request.POST.get('slide', ''))
            # for slide in mySlides:
                # mySlide = slide
            instancia = form.save(commit=False)
            instancia.user = object_instance
            instancia.save()
            Message.objects.create(
                project_id=instancia.id,
                user=object_instance,
                contenido='Bienvenidos'
            )

        return redirect(self.request.path)
    


class projectSlideDetail(generic.DetailView,FormView):
    # note = Notes.objects.all()
    template_name = "projects/projectSlide.html"
    model = ProjectSlide
    form_class = ProjectSlideForm
     

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(projectSlideDetail, self).get_context_data(**kwargs)
        context['projectSlide'] = self.get_object()
        context['plates'] = ProjectSlide.objects.filter(project=context['projectSlide'].project)
        context['apuntes'] = Notes.objects.filter(project=context['projectSlide'],show=True).order_by('id') 
        context['apuntesHidden'] = Notes.objects.filter(project=context['projectSlide'],show=False).order_by('id') 
        context['notes']=None
        context['form'] = NoteForm
        elementos = Notes.objects.exclude(geojson_data=None).filter(show=True,project=context['projectSlide']) # Recupera los modelos con el campo 'show' verdadero
        context['geojson_list'] = [{"geojson": elemento.geojson_data} for elemento in elementos]
        # context['notes'] = apuntes
        return context

    def post(self, request, *args, **kwargs):
        object_instance = self.get_object()
        
        form = NoteForm(request.POST)
        if form.is_valid():
            instancia = form.save(commit=False)
            instancia.project = object_instance
            instancia.xUnoPos = 1
            instancia.yUnoPos = 1
            instancia.xDosPos = 2
            instancia.yDosPos = 2
            instancia.show = True
            instancia.geojson_data = None
            instancia.save()
        return FormView.post(self, request, *args, **kwargs)
    
class projectDetail(generic.DetailView,FormView,DeleteView):
    # note = Notes.objects.all()
    template_name = "projects/project.html"
    model = Project
    form_class = ProjectSlideForm
    
     

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(projectDetail, self).get_context_data(**kwargs)
        projectSelf =  self.get_object()
        placas = ProjectSlide.objects.filter(project=projectSelf.project)
        catalogo = Slide.objects.all()
        idNum = self.kwargs['map']
        usuarios = projectSelf.sharedUsers
        #pk = ProjectSlide.objects.filter(project=context['pk'])
        context['form'] = ProjectSlideForm
        context['plates'] = placas
        context['catalogo'] = catalogo
        context['usuarios'] = usuarios
        
        context['slideSel'] = None
        context['slideId'] = None
        # context['make'] = str(self.kwargs['sel'])
        context['pk'] = str(self.kwargs['pk'])
      
        return context
    
    def get(self, request, *args, **kwargs):
        # context = super(projectDetail, self).get_context_data(**kwargs)
        form_b = MensajeForm
        form = ProjectSlideForm
        project = self.get_object()
        plates  = ProjectSlide.objects.filter(project=self.get_object())
        
        pk = str(self.kwargs['pk'])
        queryset = request.GET.get('buscar')
        ver = request.GET.get('ver')
        numUser = 1
        for item in project.sharedUsers.all():
            numUser = numUser + 1

        numPlacas = 0
        for item in plates:
            numPlacas = numPlacas + 1


        mapNum = self.kwargs['map']
        optionNum = self.kwargs['option']
        mapSlide = None
        geojson_list = []
        if(optionNum ==1):
            if(mapNum):
                mapSlide = ProjectSlide.objects.get(id=mapNum)
                # projec_slide_instance = ProjectSlide.objects.get(id=mapNum)
                form = ProjectSlideForm(instance=mapSlide)
                elementos = Notes.objects.exclude(geojson_data=None).filter(show=True,project=mapSlide)  # Recupera los modelos con el campo 'show' verdadero
                geojson_list = [{"geojson": elemento.geojson_data} for elemento in elementos]
        if(optionNum ==2):
                mapSlide = Slide.objects.get(id=mapNum)
        placaID = request.GET.get('placaId')
        catalogo = Slide.objects.all()
        mySlide = None
        slideName = None

        if placaID:
            mySlide = Slide.objects.get(id=placaID)
            slideName = mySlide.name
        if queryset:
            palabras = queryset.split()
            condiciones_busqueda = []

            for palabra in palabras:
                condicion = Q(name__icontains=palabra)
                condicion2 = Q(description__icontains=palabra) 
                condiciones_busqueda.append(condicion)
                condiciones_busqueda.append(condicion2)

            consulta = Q()
            for condicion in condiciones_busqueda:
                consulta |= condicion

            catalogo = Slide.objects.filter(consulta)
            
        paginator = Paginator(catalogo,30)
        user_id = request.user.id
        if ver:
            paginator = Paginator(catalogo,9)
        
        page = request.GET.get('page')
        list = Project.objects.get(id = project.id)
        member = list.sharedUsers.all()
        
        catalogo = paginator.get_page(page)
        return render(request,"projects/project.html",{'member':member,'user_id': user_id,'geojson_list':geojson_list,'catalogo':catalogo,'numPlacas':numPlacas,'numUser':numUser,'optionNum':optionNum,'mapSlide':mapSlide,'project':project,'ver':ver,'form':form,'form_b':form_b,'pk':pk,'placaId':placaID,'slideName':slideName,'plates':plates})
    
    
    def post(self, request, *args, **kwargs):
        object_instance = self.get_object() 
        idNum = self.kwargs['map']
        optionNum = self.kwargs['option']
        form_b = MensajeForm(request.POST)
        if(optionNum == 1):
            projec_slide_instance = ProjectSlide.objects.get(id= idNum )
            form = ProjectSlideForm(request.POST,instance=projec_slide_instance)
        elif(optionNum == 2):
            form = ProjectSlideForm(request.POST)
        # print('jos')
        if form.is_valid():
            instancia = form.save(commit=False)
            instancia.project = object_instance
            # instancia.placaId = request.POST.get('placaId')
            mySlide = Slide.objects.get(id=request.POST.get('slide'))
            # mySlide = None
            # # print(request.POST.get('slide', ''))
            # for slide in mySlides:
            #     mySlide = slide
            # instancia.user = object_instance
            instancia.slide = mySlide
            instancia.save()

        if form_b.is_valid():
            instancia = form_b.save(commit=False)

        return redirect(self.request.path)
    
class projectProfileDetail(generic.DetailView,FormView,DeleteView):
    # note = Notes.objects.all()
    template_name = "projects/projectProfile.html"
    model = Project
    
     

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super(projectDetail, self).get_context_data(**kwargs)
        projectSelf =  self.get_object()
        placas = ProjectSlide.objects.filter(project=projectSelf.project)
        catalogo = Slide.objects.all()
        idNum = self.kwargs['map']
        usuarios = projectSelf.sharedUsers
        #pk = ProjectSlide.objects.filter(project=context['pk'])
        context['form'] = ProjectSlideForm
        context['plates'] = placa
        context['catalogo'] = catalogo
        context['usuarios'] = usuarios
        
        context['slideSel'] = None
        context['slideId'] = None
        # context['make'] = str(self.kwargs['sel'])
        context['pk'] = str(self.kwargs['pk'])
      
        return context
    
    def get(self, request, *args, **kwargs):
        # context = super(projectDetail, self).get_context_data(**kwargs)
        
        project = self.get_object()
        plates  = ProjectSlide.objects.filter(project=self.get_object())
        
        pk = str(self.kwargs['pk'])
        queryset = request.GET.get('buscar')
        ver = request.GET.get('ver')
        numUser = 1
        for item in project.sharedUsers.all():
            numUser = numUser + 1

        numPlacas = 0
        for item in plates:
            numPlacas = numPlacas + 1


        mapNum = self.kwargs['map']
        optionNum = self.kwargs['option']
        mapSlide = None
        geojson_list = []
        if(optionNum ==1):
            if(mapNum):
                mapSlide = ProjectSlide.objects.get(id=mapNum)
                elementos = Notes.objects.exclude(geojson_data=None).filter(show=True,project=mapSlide)  # Recupera los modelos con el campo 'show' verdadero
                geojson_list = [{"geojson": elemento.geojson_data} for elemento in elementos]
        
        placaID = request.GET.get('placaId')
        mySlide = None
        slideName = None

        if placaID:
            mySlide = Slide.objects.get(id=placaID)
            slideName = mySlide.name
      
            
        list = Project.objects.get(id = project.id)
        member = list.sharedUsers.all()
        user_id = request.user.id
        
        return render(request,"projects/projectProfile.html",{'member':member,'user_id': user_id,'geojson_list':geojson_list,'numPlacas':numPlacas,'numUser':numUser,'optionNum':optionNum,'mapSlide':mapSlide,'project':project,'ver':ver,'pk':pk,'placaId':placaID,'slideName':slideName,'plates':plates})
    
    

class noteDetail(generic.DetailView):
    # no. = Notes.objects.all()
    template_name = "projects/note.html"
    model = Notes
    

    def get_context_data(self, *args, **kwargs):
        context = super(noteDetail, self).get_context_data(**kwargs)

        context['note'] = self.get_object()
        context['noteGeojson'] = self.get_object().geojson_data
        apuntes = Notes.objects.filter(project=context['note'].project)
        project = ProjectSlide.objects.get(id=self.kwargs['project_id'])
        context['apuntes'] = apuntes
        context['projectSlide'] = project
        context['apuntes'] = Notes.objects.filter(project=context['projectSlide']).order_by('id') 
        context['form'] = NoteForm
        excludeNotes = Q(geojson_data=None) | Q(id=context['note'].id)
        elementos = Notes.objects.exclude(excludeNotes).filter(show=True,project=project) # Recupera los modelos con el campo 'show' verdadero
        context['geojson_list'] = [{"geojson": elemento.geojson_data} for elemento in elementos]

        return context
    
    def post(self, request, *args, **kwargs):

        option = int(request.POST.get('option'))
        note_id = self.kwargs['pk']
        if(option==1):
            note_instance = Notes.objects.get(id= note_id )
            geojson_data = request.POST.get('geojson_data')
            form = NoteForm(request.POST,instance=note_instance)
        else:
            form = NoteForm(request.POST)
        object_instance = self.get_object().project
        if form.is_valid():
            instancia = form.save(commit=False)
            if(option):
                instancia.geojson_data = geojson_data
            else:
                instancia.project = object_instance
                instancia.xUnoPos = 1
                instancia.yUnoPos = 1
                instancia.xDosPos = 2
                instancia.yDosPos = 2
                instancia.show = True
                instancia.geojson_data = None
            instancia.save()
        new_url = '/projectSlideDetail/'+str(object_instance.id)

        return redirect(new_url)
    

def obtener_lista(request):
    # Aquí debes obtener la lista actualizada desde tu modelo o cualquier otra fuente de datos
    lista_actualizada = Notes.objects.all().values()  # Por ejemplo, obtenemos todos los objetos del modelo y los convertimos a diccionario

    # Devuelve los datos en formato JSON
    return JsonResponse(list(lista_actualizada), safe=False)

def deleteNota(request, nota_id):
    instancia = Notes.objects.get(id=nota_id)
    new_url = '/projectSlideDetail/'+str(instancia.project.id)
    instancia.delete()

    return redirect(new_url)


# def deleteProject(request, project_id):
#     instancia = Project.objects.get(id=project_id)
#     new_url = 'project-list'
#     instancia.delete()

#     return redirect(new_url)

# @login_required
def deleteProject(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Verificar si el usuario es el propietario del proyecto
    if request.user == project.user:
        project.delete()
        return redirect('project-list')  # O redirige a donde sea necesario después de borrar el proyecto
    else:
        # Devuelve una respuesta de error o redirige a otra página
        return HttpResponse("No tienes permiso para borrar este proyecto.")

# def deleteProjectSlide(request, project_id):
#     instancia = ProjectSlide.objects.get(id=project_id)
#     new_url = instancia.project.get_absolute_url()
#     instancia.delete()deleteSlide

#     return redirect(new_url)

# @login_required
def deleteProjectSlide(request, slide_id):
    slide = get_object_or_404(ProjectSlide, id=slide_id)
    # Verificar si el usuario es miembro del proyecto asociado al slide
    if request.user in slide.project.sharedUsers.all():
        slide.delete()
        return redirect('project-list')  # O redirige a donde sea necesario después de borrar el slide
    else:
        # Devuelve una respuesta de error o redirige a otra página
        return HttpResponse("No tienes permiso para borrar este slide.")

def showNote(request,project_id, note_id):
    note = Notes.objects.get(id=note_id)
    note.show = not note.show 
    note.save()
    new_url = '/projectSlideDetail/'+str(project_id)

    return redirect(new_url)

def deleteProjectUser(request, project_id,projectUser_id):
    usuario = User.objects.get(id=projectUser_id)
    proyecto = Project.objects.get(id=project_id)
    proyecto.sharedUsers.remove(usuario)
    
    new_url = '/projectDetail/'+str(project_id)+'/3/0'

    return redirect(new_url)

def newProjectUser(request, project_id,projectUser_id):

    usuario = User.objects.get(id=projectUser_id)
    proyecto = Project.objects.get(id=project_id)
    proyecto.invitedUsers.remove(usuario)
    if(proyecto.user != usuario):
        proyecto.sharedUsers.add(usuario)
    new_url = '/projectDetail/'+str(project_id)+'/1/0'

    return redirect(new_url)

def deleteProjectInvitedUser(request, project_id,projectUser_id):
    usuario = User.objects.get(id=projectUser_id)
    proyecto = Project.objects.get(id=project_id)
    proyecto.invitedUsers.remove(usuario)
    
    new_url = '/project-list/'

    return redirect(new_url)

def newProjectInvitedUser(request, project_id,projectUser_id):

    usuario = User.objects.get(id=projectUser_id)
    proyecto = Project.objects.get(id=project_id)
    if(proyecto.user != usuario):
        proyecto.invitedUsers.add(usuario)
    new_url = '/projectDetail/'+str(project_id)+'/3/0'

    return redirect(new_url)

def datos_actualizados_catalogo(request,*args, **kwargs):
    

    queryset = kwargs.get('buscar', None)
    items = Slide.objects.filter( assembled=True)
    if queryset and not queryset == '_':
        palabras = queryset.split()
        condiciones_busqueda = []

        for palabra in palabras:
            condicion = Q(name__icontains=palabra)
            condicion2 = Q(description__icontains=palabra) 
            condiciones_busqueda.append(condicion)
            condiciones_busqueda.append(condicion2)

        consulta = Q()
        for condicion in condiciones_busqueda:
            consulta |= condicion

        items = Slide.objects.filter(consulta)
        
    paginator = Paginator(items,9)
    
    page = request.GET.get('page')
        
        
    items= paginator.get_page(page)
    
    nombres = [item.name for item in items]
    idList = [item.id for item in items]
    imagenes = [item.image.url for item in items]
    descripcion = [item.description for item in items]

    return JsonResponse({'name':nombres,'id':idList,'image':imagenes,'description':descripcion}, safe=False)  

def datos_actualizados_placas(request,*args, **kwargs):

    project= kwargs.get('project', None)
    items =  ProjectSlide.objects.filter(project = project) 
    queryset = kwargs.get('buscar', None)
    if queryset and not queryset == '_':
        palabras = queryset.split()
        condiciones_busqueda = []

        for palabra in palabras:
            condicion = Q(name__icontains=palabra)
            condicion2 = Q(description__icontains=palabra) 
            condiciones_busqueda.append(condicion)
            condiciones_busqueda.append(condicion2)

        

        consulta = Q()
        for condicion in condiciones_busqueda:
            consulta |= condicion
        
        consulta &= Q(project = project)

        items =  ProjectSlide.objects.filter(consulta)
        
    paginator = Paginator(items,9)
    
    page = request.GET.get('page')
        
        
    items= paginator.get_page(page)
    nombres = [item.name for item in items]
    idList = [item.id for item in items]
    
    return JsonResponse({'name':nombres,'id':idList}, safe=False)  



def datos_actualizados_colaboradores(request,*args, **kwargs):
    queryset = kwargs.get('buscar', None)
    itemsBuscar = None
    nombres= None
    idList = None
    fullname = None
    project= kwargs.get('project', None)
    list = Project.objects.get(id = project)

    if queryset and not queryset == '_':
        palabras = queryset.split()
        condiciones_busqueda = []

        for palabra in palabras:
            condicion = Q(username__icontains=palabra)
            # condicion2 = Q(description__icontains=palabra) 
            condiciones_busqueda.append(condicion)
            # condiciones_busqueda.append(condicion2)

        consulta = Q()
        for condicion in condiciones_busqueda:
            consulta |= condicion
        shared_user_ids = list.sharedUsers.values_list('id', flat=True)
        invited_user_ids = list.invitedUsers.values_list('id', flat=True)
        
        # Construye la consulta para excluir usuarios por ID
        exclude = Q(id__in=shared_user_ids) | Q(id=list.user.id) | Q(id__in=invited_user_ids)

        # Filtra los usuarios basados en la consulta
        itemsBuscar = User.objects.exclude(exclude).filter(consulta)
        
        paginator = Paginator(itemsBuscar,9)    
        page = request.GET.get('page')
        itemsBuscar= paginator.get_page(page)
        nombres = [item.username for item in itemsBuscar]
        idList = [item.id for item in itemsBuscar]
        fullname = [str(item.first_name)+' '+str(item.last_name) for item in itemsBuscar]

    invitedMember = list.invitedUsers.all()
    nombresInvite = [item.username for item in invitedMember]
    idListInvite = [item.id for item in invitedMember]
    fullnameInvite = [str(item.first_name)+' '+str(item.last_name) for item in invitedMember]

    ownerID = list.user.id
    ownerN = list.user.username

    return JsonResponse({'fullnameInvite':fullnameInvite,'nameInvite':nombresInvite,'fullname':fullname,'ownerN':ownerN,'idInvite':idListInvite,'ownerID':ownerID,'name':nombres,'id':idList}, safe=False)  

def datos_actualizados_chat(request,*args, **kwargs):
    queryset = kwargs.get('buscar', None)
    itemsBuscar = None
    meessages= None
    messageDate = None
    project= kwargs.get('project', None)
    list = Message.objects.filter(project = project).order_by('fecha_envio')

    # if queryset and not queryset == '_':
    #     palabras = queryset.split()
    #     condiciones_busqueda = []

    #     for palabra in palabras:
    #         condicion = Q(username__icontains=palabra)
    #         # condicion2 = Q(description__icontains=palabra) 
    #         condiciones_busqueda.append(condicion)
    #         # condiciones_busqueda.append(condicion2)

    #     consulta = Q()
    #     for condicion in condiciones_busqueda:
    #         consulta |= condicion
    #     shared_user_ids = list.sharedUsers.values_list('id', flat=True)
    #     invited_user_ids = list.invitedUsers.values_list('id', flat=True)
        
    #     # Construye la consulta para excluir usuarios por ID
    #     exclude = Q(id__in=shared_user_ids) | Q(id=list.user.id) | Q(id__in=invited_user_ids)

    #     # Filtra los usuarios basados en la consulta
    #     itemsBuscar = User.objects.exclude(exclude).filter(consulta)
        
    #     paginator = Paginator(itemsBuscar,9)    
    #     page = request.GET.get('page')
    #     itemsBuscar= paginator.get_page(page)
    #     nombres = [item.username for item in itemsBuscar]
    #     idList = [item.id for item in itemsBuscar]
    #     fullname = [str(item.first_name)+' '+str(item.last_name) for item in itemsBuscar]

    
    name = [item.user.username for item in list]
    meessage = [item.contenido for item in list]
    # date = [timezone.make_aware(item.fecha_envio).strftime("%I:%M %p") for item in list]
    date = [(timezone.make_aware(item.fecha_envio).strftime("%Y-%m-%d"), timezone.make_aware(item.fecha_envio).strftime("%I:%M %p")) for item in list]

    userid = [item.user.id for item in list]

    return JsonResponse({'meessages':meessage,'name':name,'date':date,'userId':userid}, safe=False)  