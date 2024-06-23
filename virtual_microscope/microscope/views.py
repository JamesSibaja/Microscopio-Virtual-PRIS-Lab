from django.shortcuts import render, redirect
from microscope.models import Slide,OpenSlide, ProcessingHistory
from django.views.generic import CreateView
from django.views import generic
from django.template import Template, context
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import FormView
from .forms import  UploadFileForm, SlideForm
from .tasks import convert_to_tiles
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.files.base import ContentFile
import os
import logging
from django.http import HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import shutil
from celery.result import AsyncResult


UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'archivo')

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@csrf_exempt
def upload_view(request):
    if request.method == 'POST':
        os.makedirs('media/archivo/', exist_ok=True)
        file = request.FILES['archivo']
        chunk_index = int(request.POST['chunkIndex'])
        total_chunks = int(request.POST['totalChunks'])
        file_name = request.POST['fileName']+ '_' + str(OpenSlide.objects.count())
        name = request.POST['name']

        temp_file_path = os.path.join(UPLOAD_DIR, f'{file_name}.part{chunk_index}')
        with default_storage.open(temp_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        if chunk_index + 1 == total_chunks:
            # Ensamblar los chunks en el archivo final
            final_file_path = os.path.join(UPLOAD_DIR, file_name)
            with default_storage.open(final_file_path, 'wb+') as final_file:
                for i in range(total_chunks):
                    temp_file_path = os.path.join(UPLOAD_DIR, f'{file_name}.part{i}')
                    with default_storage.open(temp_file_path, 'rb') as temp_file:
                        final_file.write(temp_file.read())
                    os.remove(temp_file_path)
            instance = OpenSlide(name=name)
            instance.save()
            instance.path = final_file_path
            instance.save()
            return JsonResponse({'message': 'Archivo subido correctamente'})

        return JsonResponse({'message': 'Chunk recibido correctamente'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Configura la configuración de registro según tus necesidades
logger = logging.getLogger('myapp.view') 
# Create your views here.

class micro(generic.DetailView):
    template_name = "microscope/microscopio.html"
    model = Slide

class microfull(generic.DetailView):
    template_name = "microscope/microscopiofull.html"
    model = Slide

def task_status(request, task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'error': str(task.info),  # Esto es el traceback
        }
    return JsonResponse(response)

def catalogo(request):
    queryset = request.GET.get('buscar')
    # ver = request.GET.get('ver')
    catalogo = Slide.objects.filter( assembled=True)
    
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
        
    # paginator = Paginator(catalogo,30)

    paginator = Paginator(catalogo,9)
    
    page = request.GET.get('page')
    catalogo = paginator.get_page(page)

    return render(request,"microscope/catalogo.html",{'catalogo':catalogo})

def catalogo_edit(request, delete_edit):
    queryset = request.GET.get('buscar')
    catalogo = Slide.objects.filter(assembled=True)
    
    if request.method == 'POST':
        slide_id = request.POST.get('slide_id')
        slide = get_object_or_404(Slide, id=slide_id)
        form = SlideForm(request.POST, instance=slide)
        if form.is_valid():
            form.save()
            return redirect('Catalogo_edit', delete_edit=delete_edit)
    else:
        form = SlideForm()

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

    paginator = Paginator(catalogo, 9)
    page = request.GET.get('page')
    catalogo = paginator.get_page(page)

    return render(request, "microscope/catalogo_edit.html", {
        'catalogo': catalogo,
        'delete_edit': delete_edit,
        'form': form
    })

def get_slide_data(request, slide_id):
    slide = get_object_or_404(Slide, id=slide_id)
    data = {
        'id': slide.id,
        'name': slide.name,
        'description': slide.description,
    }
    return JsonResponse(data)

def upload_file(request):
    listSlide = OpenSlide.objects.filter(assembled=False).distinct()

    if request.method == 'POST':
        option = int(request.POST.get('option'))
        form = SlideForm(request.POST, request.FILES)
        if form.is_valid():
            rawSlide = OpenSlide.objects.get(id=int(request.POST.get('slide')))
            rawSlide.assembled = True
            rawSlide.save()
            instance = form.save(commit=False)
            instance.save()
            instance.rawSlide = rawSlide
            instance.image = 'slides/slide' + str(instance.id) + '/1/0.jpg'
            instance.path = 'slide' + str(instance.id)
            instance.save()

            # Llamar a la tarea asíncrona para convertir a mosaico
            task = convert_to_tiles.delay(rawSlide.path, 'media/slides/slide' + str(instance.id), instance.rawSlide.id, instance.id, request.user.id)
            instance.task_id = task.id
            instance.save()

            return render(request, 'microscope/subir_archivo.html', {'form': form, 'listSlide': listSlide})

        else:
            return JsonResponse(form.errors, status=400)

    else:
        form = SlideForm()

    return render(request, 'microscope/subir_archivo.html', {'form': form, 'listSlide': listSlide})


def activity_log(request):
    listSlideError = ProcessingHistory.objects.filter(end_time__isnull=False).order_by('-end_time')
    return render(request, 'microscope/activity_log.html', {'listSlide':listSlideError})

def processing(request):
    listSlide = Slide.objects.filter(assembled=False,error=False).distinct()
    listSlideError = Slide.objects.filter(error=True).distinct()

    return render(request, 'microscope/procesando.html', {'listSlide':listSlide,'listSlideError':listSlideError})

def delete(request, slide_id):
    instancia = OpenSlide.objects.get(id=slide_id)
    folder_path = instancia.path
    if os.path.isfile(folder_path):
        os.remove(folder_path)
    new_url = '/upload_file/'
    instancia.delete()

    return redirect(new_url)

# @login_required
# @require_http_methods(["POST"])
def reset_slide(request, slide_id):
    slide = get_object_or_404(ProcessingHistory, id=slide_id)
    if slide.raw_slide:
        raw_slide = slide.raw_slide
        raw_slide.assembled = False
        raw_slide.save()
    return JsonResponse({'success': True})

def historial_detalles(request, id):
    history_entry = get_object_or_404(ProcessingHistory, id=id)
    data = {
        'file_name': history_entry.file_name,
        'user': history_entry.user.username,
        'status': history_entry.get_status_display(),
        'start_time': history_entry.start_time.strftime('%Y-%m-%d %H:%M:%S') if history_entry.start_time else '',
        'end_time':         history_entry.end_time.strftime('%Y-%m-%d %H:%M:%S') if history_entry.end_time else '',
        'duration': history_entry.duration,
        'error_message': history_entry.error_message,
        'raw_slide': history_entry.raw_slide.name if history_entry.raw_slide else None
    }
    return JsonResponse(data)

def deleteSlide(request, slide_id):
    instancia = get_object_or_404(Slide, id=slide_id)
    instancia.rawSlide.assembled = False
    instancia.rawSlide.save()
    base_media_path = os.path.join(settings.MEDIA_ROOT, 'slides')
    folder_path = os.path.join(base_media_path, instancia.path)
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)

    # Eliminar la instancia del catálogo
    instancia.delete()

    # Redirigir a la URL deseada
    new_url = '/catalogo_edit/1/'
    return redirect(new_url)

