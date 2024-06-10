from celery import shared_task
from django.utils import timezone
import os
import shutil
import openslide
import math
from .models import Slide, OpenSlide, ProcessingHistory,User

@shared_task(bind=True)
def convert_to_tiles(self, input_path, output_path, idOpenSLide, idSlide, user_slide ,tile_size=256):
    # Crear una entrada en el historial de procesamiento
    microscopeSlide = Slide.objects.get(id=idSlide)
    user = User.objects.get(id= user_slide ) # Asume que hay un campo `user` en el modelo Slide que relaciona con el usuario

    history_entry = ProcessingHistory.objects.create(
        user=user,
        file_name=os.path.basename(input_path),
        status='FAILURE'  # Inicialmente se marca como fallo hasta que se complete con éxito
    )

    try:
        slide = openslide.open_slide(input_path)
        mpp_x = float(slide.properties[openslide.PROPERTY_NAME_MPP_X])
        mpp_y = float(slide.properties[openslide.PROPERTY_NAME_MPP_Y])
        
        slide_width, slide_height = slide.dimensions
        num_levels = slide.level_count
        resolution = 1 / max(slide_width, slide_height)
        quotient = 1 - resolution
        
        maxlatlng = 90 - math.degrees(math.asin(quotient))
        minZoom = math.ceil(math.log2(90 / maxlatlng))

        os.makedirs(output_path, exist_ok=True)
        base_level = math.ceil(math.log(max(slide_width, slide_height) / tile_size, 2))
        total_tiles = pow(pow(2, base_level), 2)
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': total_tiles})

        pixxm = (40075000 / (tile_size * pow(2, minZoom + base_level))) * slide_width
        factor = ((tile_size * pow(2, minZoom + base_level)) / 40075000) * ((mpp_x + mpp_y) / 2)

        if base_level > num_levels:
            minZoom = minZoom + base_level - num_levels
            base_level = num_levels

        slide_widthZ0, slide_heightZ0 = slide.level_dimensions[base_level - 1]
        offsetx = ((slide_width / (math.ceil(slide_widthZ0 / tile_size) * tile_size * slide.level_downsamples[base_level - 1])) - 1) * (180 / pow(2, minZoom))
        offsety = (1 - (slide_height / (math.ceil(slide_heightZ0 / tile_size) * tile_size * slide.level_downsamples[base_level - 1]))) * (90 / pow(2, minZoom))
        xy_base_level_folder = pow(2, (minZoom)) - 1

        row_folderII = os.path.join(output_path, str(1))
        os.makedirs(row_folderII, exist_ok=True)
        thumbnail = slide.get_thumbnail((256, 256))
        tile_filename = os.path.join(row_folderII, f"{0}.jpg")
        thumbnail.save(tile_filename, "JPEG")
        processed_tiles = 0
        for level in range(num_levels):
            level_width, level_height = slide.level_dimensions[level]
            level_downsample = slide.level_downsamples[level]
            num_level_folder = base_level - level
            level_folder = os.path.join(output_path, str(num_level_folder + minZoom))
            xy_level_folder = xy_base_level_folder * pow(2, num_level_folder - 1)
            
            if num_level_folder > 0:
                os.makedirs(level_folder, exist_ok=True)
                
                rows = math.ceil(level_height / tile_size)
                cols = math.ceil(level_width / tile_size)

                for row in range(rows):
                    row_folder = os.path.join(level_folder, f"{row + xy_level_folder}")
                    os.makedirs(row_folder, exist_ok=True)

                    for col in range(cols):
                        x = col * tile_size * int(level_downsample)
                        y = row * tile_size * int(level_downsample)
                        
                        tile = slide.read_region((x, y), level, (tile_size, tile_size))
                        tile = tile.convert("RGB")
                        
                        tile_filename = os.path.join(row_folder, f"{col + xy_level_folder}.jpg")
                        tile.save(tile_filename, "JPEG")
                        processed_tiles += 1
                        self.update_state(state='PROGRESS', meta={'current': processed_tiles, 'total': total_tiles})


        rawSlide = OpenSlide.objects.get(id=idOpenSLide)
        microscopeSlide.assembled = True
        microscopeSlide.zoomM = base_level + minZoom
        microscopeSlide.zoomI = minZoom + 2
        microscopeSlide.zoomMin = minZoom + 1
        microscopeSlide.centerLat = offsety
        microscopeSlide.centerLng = offsetx
        microscopeSlide.maxLatLng = 2 * maxlatlng
        microscopeSlide.factor = factor
        rawSlide.assembled = True
        rawSlide.save()
        microscopeSlide.save()
        slide.close()

        # Actualizar el historial de procesamiento a éxito
        history_entry.status = 'SUCCESS'
        history_entry.end_time = timezone.now()
        history_entry.save()

        return {'current': total_tiles, 'total': total_tiles, 'status': 'Task completed!'}

    except Exception as e:
        try:
            shutil.rmtree(output_path)
        except:
            print("Directorio no existe")

        os.remove(input_path)
        microscopeSlide.error = True
        microscopeSlide.save()
        print(f"An error occurred: {str(e)}")

        # Actualizar el historial de procesamiento con el mensaje de error
        history_entry.error_message = str(e)
        history_entry.end_time = timezone.now()
        history_entry.save()

        return f"Error: {str(e)}"
