from django.shortcuts import render, redirect
from microscope.models import Slide,OpenSlide, ProcessingHistory
from django.views.generic import CreateView
from django.views import generic
from django.template import Template, context
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.shortcuts import render
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
from django.shortcuts import redirect, get_object_or_404

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
# def upload_view(request):
#     if request.method == 'POST' and request.FILES['archivo']:
#         archivo = request.FILES['archivo']
#         # Verificar el tamaño del archivo
#         if archivo.size <= settings.MAX_UPLOAD_SIZE:
#             # Guardar el archivo en chunks
#             ruta_temporal = 'archivo_temporal'
#             with open(ruta_temporal, 'wb+') as destino:
#                 for chunk in archivo.chunks():
#                     destino.write(chunk)
#             # Hacer algo con los chunks (por ejemplo, ensamblarlos)
#             # Aquí ensamblamos los chunks en un solo archivo
#             with open(ruta_temporal, 'rb') as archivo_chunks:
#                 with open('archivo_final', 'wb') as archivo_final:
#                     for chunk in archivo_chunks:
#                         archivo_final.write(chunk)
#             # Eliminar el archivo temporal de chunks
#             os.remove(ruta_temporal)
#             return JsonResponse({'message': 'Archivo subido correctamente'})
#         else:
#             return JsonResponse({'error': 'El tamaño del archivo excede el límite permitido'})
#     else:
#         return JsonResponse({'error': 'Se requiere un archivo para subir'})
# from django.views.decorators.csrf import csrf_exempt
# from filetransfers.api import serve_file
# from myapp.models import MyModel
# # import ftplib
# # import paramiko




# Configura la configuración de registro según tus necesidades
logger = logging.getLogger('myapp.view') 
# Create your views here.


# def upload_ftp(request):
#     if request.method == 'POST' and request.FILES:
#         file = request.FILES['file']
#         file_name = file.name
#         try:
#             ftp = ftplib.FTP(settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASSWORD)
#             with file.open() as f:
#                 ftp.storbinary(f'STOR {file_name}', f)
#             ftp.quit()
#             return HttpResponse('Archivo cargado exitosamente')
#         except Exception as e:
#             return HttpResponseBadRequest(f'Error al cargar el archivo: {str(e)}')
#     else:
#         return HttpResponseBadRequest('Se esperaba un archivo en la solicitud')

class micro(generic.DetailView):
    template_name = "microscope/microscopio.html"
    model = Slide

class microfull(generic.DetailView):
    template_name = "microscope/microscopiofull.html"
    model = Slide

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

def catalogo_edit(request,delete_edit):
    queryset = request.GET.get('buscar')
    # ver = request.GET.get('ver')
    catalogo = Slide.objects.filter( assembled=True)
    form = SlideForm(request.POST, request.FILES)
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

    return render(request,"microscope/catalogo_edit.html",{'catalogo':catalogo,'delete_edit':delete_edit})

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

def upload_file(request):
    listSlide = OpenSlide.objects.filter(assembled=False).distinct()

    if request.method == 'POST': #Aqui se suben los archivos
        option = int(request.POST.get('option'))
        form = SlideForm(request.POST, request.FILES)
        if form.is_valid():
            option = int(request.POST.get('option'))
            rawSlide = OpenSlide.objects.get(id=int(request.POST.get('slide')))
            rawSlide.assembled = True
            rawSlide.save()
            instance = form.save(commit=False)
            instance.save()
            instance.rawSlide = rawSlide
            instance.image = 'slides/slide' +str(instance.id)+'/1/0.jpg'
            instance.path = 'slide' +str(instance.id)
            instance.save()

            # Llamar a la tarea asíncrona para convertir a mosaico
            convert_to_tiles.delay(rawSlide.path, 'media/slides/slide' +str(instance.id), instance.rawSlide.id, instance.id,request.user.id)
        else:
            return JsonResponse(form.errors, status=400)  # Devuelve errores de validación

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

def historial_detalles(request, id):
    history_entry = get_object_or_404(ProcessingHistory, id=id)
    data = {
        'file_name': history_entry.file_name,
        'user': history_entry.user.username,
        'status': history_entry.get_status_display(),
        'start_time': history_entry.start_time,
        'end_time': history_entry.end_time,
        'duration': history_entry.duration,
        'error_message': history_entry.error_message,
    }
    return JsonResponse(data)
# Conexión al servidor SFTP
# def sftp_connect():
#     host = 'localhost'
#     port = 2222
#     username = 'sftpuser'
#     # Cambiar la ruta de la clave privada
#     private_key_path = f'/etc/ssh/keys/{username}_private.pem'

#     # Cargando la clave privada del usuario
#     key = paramiko.RSAKey.from_private_key_file(private_key_path)

#     transport = paramiko.Transport((host, port))
#     transport.connect(username=username, pkey=key)

#     sftp = paramiko.SFTPClient.from_transport(transport)
#     return sftp

# # Subir archivo al servidor SFTP
# def upload_file_to_sftp(local_path, remote_path):
#     try:
#         sftp = sftp_connect()
#         sftp.put(local_path, remote_path)
#         sftp.close()
#         return True
#     except Exception as e:
#         print(f'Error al subir archivo al servidor SFTP: {e}')
#         return False
 # Obtener el archivo del formulario
            # uploaded_file = request.POST.get('file_name')
            # # Directorio del usuario donde se encuentra el archivo
            # user_directory = request.FILES.get('user_directory')
            # # Construir la ruta completa del archivo del usuario
            # user_file_path = os.path.join(user_directory, uploaded_file.name)
            # # Construir la ruta donde se guardará en el servidor
            # server_file_path = os.path.join('media/archivo', f'{instance.id}_{uploaded_file.name}')

            # # Subir archivo al servidor SFTP
            # if upload_file_to_sftp(user_file_path, server_file_path):
            #     instance = OpenSlide(name=uploaded_file.name)
            #     instance.save()
            #     instance.path = server_file_path
            #     instance.save()
            #     response_data = {'message': 'Archivo cargado exitosamente'}
            # else:
            #     response_data = {'message': 'Error al subir archivo al servidor SFTP'}
            # return JsonResponse(response_data)