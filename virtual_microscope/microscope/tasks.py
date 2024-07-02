from celery import shared_task
from django.utils import timezone
import os
import shutil
import zipfile
import openslide
import math
from .models import Slide, OpenSlide, ProcessingHistory, User
from PIL import Image
from collections import Counter

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_most_common_color(image, slide = None):
    width, height = image.size
    pixels = []

    for x in range(width):
        pixels.append(image.getpixel((x, 0)))  # Top edge
        pixels.append(image.getpixel((x, height - 1)))  # Bottom edge

    for y in range(height):
        pixels.append(image.getpixel((0, y)))  # Left edge
        pixels.append(image.getpixel((width - 1, y)))  # Right edge

    background = Counter(pixels).most_common(1)[0][0]
    background_color = rgb2hex(background[0], background[1], background[2])
    if slide:
        slide.color = background_color
        slide.save()
    return background

def is_zipfile(filepath):
    return zipfile.is_zipfile(filepath)

def extract_zipfile(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def find_openslide_files(directory):
    allowed_extensions = ['.svs', '.tiff', '.vms', '.vmu', '.ndpi', '.scn', '.mrxs', '.tif', '.bif', '.zi', '.dcm']
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in allowed_extensions):
                files.append(os.path.join(root, filename))
    return files

@shared_task(bind=True)
def convert_to_tiles(self, input_path, output_path, idOpenSLide, idSlide, user_slide, tile_size=256):
    microscopeSlide = Slide.objects.get(id=idSlide)
    user = User.objects.get(id=user_slide)
    rawSlide = OpenSlide.objects.get(id=idOpenSLide)

    history_entry = ProcessingHistory.objects.create(
        user=user,
        file_name=rawSlide.name,
        raw_slide=rawSlide,
        status='FAILURE'
    )

    try:
        if is_zipfile(input_path):
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            zip_dir = os.path.join(os.path.dirname(input_path), base_name)
            os.makedirs(zip_dir, exist_ok=True)
            extract_zipfile(input_path, zip_dir)
            extracted_items = os.listdir(zip_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(zip_dir, extracted_items[0])):
                zip_dir = os.path.join(zip_dir, extracted_items[0])

            slide_files = find_openslide_files(zip_dir)
            if not slide_files:
                raise FileNotFoundError("No compatible OpenSlide files found in the extracted directory")

            slide_path = slide_files[0]
        else:
            slide_path = input_path

        slide = openslide.OpenSlide(slide_path)
        mpp_x = float(slide.properties[openslide.PROPERTY_NAME_MPP_X])
        mpp_y = float(slide.properties[openslide.PROPERTY_NAME_MPP_Y])
        if not mpp_x:
            raise FileNotFoundError("No metadatos")
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

        factor = ((tile_size * pow(2, minZoom + base_level)) / 40075000) * ((mpp_x + mpp_y) / 2)

        if base_level > num_levels:
            minZoom = minZoom + base_level - num_levels
            base_level = num_levels

        row_folderII = os.path.join(output_path, str(1))
        os.makedirs(row_folderII, exist_ok=True)
        thumbnail = slide.get_thumbnail((256, 256))
        tile_filename = os.path.join(row_folderII, f"{0}.jpg")
        thumbnail.save(tile_filename, "JPEG")
        thumbnail = thumbnail.convert("RGB")

        if microscopeSlide.color == None:
            background_color = get_most_common_color(thumbnail,microscopeSlide)
            background = background_color
        else:
            background_color = microscopeSlide.color
            background = get_most_common_color(thumbnail)
        
        tile_width, tile_height = thumbnail.size
        if tile_width < tile_size or tile_height < tile_size:
            new_tile = Image.new("RGB", (tile_size, tile_size), background)
            new_tile.paste(thumbnail, (math.ceil((tile_size - tile_width) / 2), math.ceil((tile_size - tile_height) / 2)))
            thumbnail = new_tile
        thumbnail.save(tile_filename, "JPEG")
        processed_tiles = 0

        # level_width, level_height = slide.level_dimensions[base_level]
        # tile = slide.read_region((0, 0), base_level, (level_width, level_height))
        # tile = tile.convert("RGB")
        # background_color = get_most_common_color(tile,microscopeSlide)

        for level in range(num_levels):
            level_width, level_height = slide.level_dimensions[level]
            level_downsample = slide.level_downsamples[level]
            num_level_folder = base_level - level
            level_folder = os.path.join(output_path, str(num_level_folder + minZoom))

            os.makedirs(level_folder, exist_ok=True)
            rowsMod = level_height % (tile_size * 2)
            colsMod = level_width % (tile_size * 2)

            rows = (level_height // (tile_size * 2)) * 2
            cols = (level_width // (tile_size * 2)) * 2

            offsetx = math.ceil(((tile_size * 2) - colsMod) / 2)
            offsety = math.ceil(((tile_size * 2) - rowsMod) / 2)
            if rowsMod > 0:
                rows += 2
            else:
                offsety = 0

            if colsMod > 0:
                cols += 2
            else:
                offsetx = 0

            y_level_folder = int((pow(2, num_level_folder + minZoom) - rows) / 2)
            x_level_folder = int((pow(2, num_level_folder + minZoom) - cols) / 2)

            for row in range(rows):
                row_folder = os.path.join(level_folder, f"{row + y_level_folder}")
                os.makedirs(row_folder, exist_ok=True)

                for col in range(cols):
                    x = (col * tile_size - offsetx) * int(level_downsample)
                    y = (row * tile_size - offsety) * int(level_downsample)
                    tile_size_y_fit = tile_size
                    tile_size_x_fit = tile_size
                    tile_fit_y = 0
                    tile_fit_x = 0
                    if row == 0:
                        y = 0
                        tile_fit_y = offsety
                    if row == rows - 1 or row == 0:
                        tile_size_y_fit = tile_size - offsety

                    if col == 0:
                        x = 0
                        tile_fit_x = offsetx
                    if col == cols - 1 or col == 0:
                        tile_size_x_fit = tile_size - offsetx

                    tile = slide.read_region((x, y), level, (tile_size_x_fit, tile_size_y_fit))
                    tile = tile.convert("RGB")

                    tile_width, tile_height = tile.size
                    if tile_width < tile_size or tile_height < tile_size:
                        new_tile = Image.new("RGB", (tile_size, tile_size), background_color)
                        new_tile.paste(tile, (tile_fit_x, tile_fit_y))
                        tile = new_tile

                    tile_filename = os.path.join(row_folder, f"{col + x_level_folder}.jpg")
                    tile.save(tile_filename, "JPEG")
                    processed_tiles += 1
                    self.update_state(state='PROGRESS', meta={'current': processed_tiles, 'total': total_tiles})

        microscopeSlide.assembled = True
        microscopeSlide.zoomM = base_level + minZoom
        microscopeSlide.zoomI = minZoom + 2
        microscopeSlide.zoomMin = base_level + minZoom - num_levels + 1
        microscopeSlide.maxLatLng = 2 * maxlatlng
        microscopeSlide.factor = factor
        rawSlide.assembled = True
        rawSlide.save()
        microscopeSlide.save()
        slide.close()

        history_entry.status = 'SUCCESS'
        history_entry.end_time = timezone.now()
        history_entry.save()

        return {'current': total_tiles, 'total': total_tiles, 'status': 'Task completed!'}

    except Exception as e:
        try:
            shutil.rmtree(output_path)
        except:
            print("Directorio no existe")
        microscopeSlide.delete()
        print(f"An error occurred: {str(e)}")

        history_entry.error_message = str(e)
        history_entry.end_time = timezone.now()
        history_entry.save()

        return f"Error: {str(e)}"