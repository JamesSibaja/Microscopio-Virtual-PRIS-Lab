from celery import shared_task
from django.utils import timezone
import os
import shutil
import openslide
import math
from .models import Slide, OpenSlide, ProcessingHistory,User
from PIL import Image

@shared_task(bind=True)
def convert_to_tiles(self, input_path, output_path, idOpenSLide, idSlide, user_slide ,tile_size=256):
    # Crear una entrada en el historial de procesamiento
    microscopeSlide = Slide.objects.get(id=idSlide)
    user = User.objects.get(id= user_slide ) # Asume que hay un campo `user` en el modelo Slide que relaciona con el usuario
    rawSlide = OpenSlide.objects.get(id=idOpenSLide)

    history_entry = ProcessingHistory.objects.create(
        user=user,
        file_name=rawSlide.name,
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

        # pixxm = (40075000 / (tile_size * pow(2, minZoom + base_level))) * slide_width
        factor = ((tile_size * pow(2, minZoom + base_level)) / 40075000) * ((mpp_x + mpp_y) / 2)

        if base_level > num_levels:
            minZoom = minZoom + base_level - num_levels
            base_level = num_levels

        # slide_widthZ0, slide_heightZ0 = slide.level_dimensions[base_level - 1]
        # offsetx = ((slide_width / (math.ceil(slide_widthZ0 / tile_size) * tile_size * slide.level_downsamples[base_level - 1])) - 1) * (180 / pow(2, minZoom))
        # offsety = (1 - (slide_height / (math.ceil(slide_widthZ0 / tile_size) * tile_size * slide.level_downsamples[base_level - 1]))) * (90 / pow(2, minZoom))
        # xy_base_level_folder = pow(2, (minZoom)) - 1

        row_folderII = os.path.join(output_path, str(1))
        os.makedirs(row_folderII, exist_ok=True)
        thumbnail = slide.get_thumbnail((256, 256))
        tile_filename = os.path.join(row_folderII, f"{0}.jpg")
        thumbnail.save(tile_filename, "JPEG")
        thumbnail = thumbnail.convert("RGB")

        tile_width, tile_height = thumbnail.size
        if tile_width < tile_size or tile_height < tile_size:
            new_tile = Image.new("RGB", (tile_size, tile_size), (220, 218, 229))
            new_tile.paste(tile, (math.ceil((tile_size-tile_width)/2), math.ceil((tile_size-tile_height)/2)))
            tile = new_tile
        processed_tiles = 0

        for level in range(num_levels):
            level_width, level_height = slide.level_dimensions[level]
            level_downsample = slide.level_downsamples[level]
            num_level_folder = base_level - level
            level_folder = os.path.join(output_path, str(num_level_folder + minZoom))
            
            # if num_level_folder > 0:
            os.makedirs(level_folder, exist_ok=True)
            rowsMod = level_height % (tile_size*2)
            colsMod = level_width % (tile_size*2)
            
            rows = (level_height // (tile_size*2))*2
            cols = (level_width // (tile_size*2))*2
            
            offsetx=math.ceil(((tile_size*2)-colsMod)/2)
            offsety=math.ceil(((tile_size*2)-rowsMod)/2)
            if rowsMod > 0:
                rows = rows+2
            else:
                offsety = 0

            if colsMod > 0:
                cols = cols+2
            else:
                offsetx = 0

            y_level_folder =int((pow(2, num_level_folder + minZoom ) - rows)/2)
            x_level_folder =int((pow(2, num_level_folder + minZoom) - cols)/2)

            for row in range(rows):
                row_folder = os.path.join(level_folder, f"{row + y_level_folder}")
                os.makedirs(row_folder, exist_ok=True)

                for col in range(cols):
                    x = (col * tile_size - offsetx)*int(level_downsample)
                    y = (row * tile_size  - offsety)*int(level_downsample)
                    tile_size_y_fit = tile_size
                    tile_size_x_fit = tile_size
                    tile_fit_y = 0
                    tile_fit_x = 0
                    if(row == 0):
                        y = 0
                        tile_fit_y = offsety
                    if(row == rows -1 or row == 0):
                        tile_size_y_fit = tile_size-offsety

                    if(col == 0):
                        x = 0
                        tile_fit_x = offsetx
                    if(col == cols -1 or col == 0 ):
                        tile_size_x_fit = tile_size-offsetx
                    
                    tile = slide.read_region((x, y), level, (tile_size_x_fit, tile_size_y_fit))
                    tile = tile.convert("RGB")

                    tile_width, tile_height = tile.size
                    if tile_width < tile_size or tile_height < tile_size:
                        new_tile = Image.new("RGB", (tile_size, tile_size), (220, 218, 229))
                        new_tile.paste(tile, (tile_fit_x, tile_fit_y))
                        tile = new_tile
                    
                    tile_filename = os.path.join(row_folder, f"{col + x_level_folder}.jpg")
                    tile.save(tile_filename, "JPEG")
                    processed_tiles += 1
                    self.update_state(state='PROGRESS', meta={'current': processed_tiles, 'total': total_tiles})

        microscopeSlide.assembled = True
        microscopeSlide.zoomM = base_level + minZoom
        microscopeSlide.zoomI = minZoom + 2
        microscopeSlide.zoomMin = base_level + minZoom -num_levels + 1
        # microscopeSlide.centerLat = offsety
        # microscopeSlide.centerLng = offsetx
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

        
        microscopeSlide.error = True
        microscopeSlide.save()
        print(f"An error occurred: {str(e)}")

        # Actualizar el historial de procesamiento con el mensaje de error
        history_entry.error_message = str(e)
        history_entry.end_time = timezone.now()
        history_entry.save()

        return f"Error: {str(e)}"
