import os
import re
import subprocess
import imageio_ffmpeg
from django.conf import settings
from .models import VideoTask
from django.core.files import File

def parse_time(time_str):
    """Convierte HH:MM:SS.ms en segundos flotante."""
    parts = time_str.split(':')
    if len(parts) != 3:
        return 0.0
    h, m, s = parts
    return float(h) * 3600 + float(m) * 60 + float(s)

def compress_video(task_id, quality='medium'):
    try:
        task = VideoTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()
        
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        input_path = task.original_file.path
        filename_base = os.path.basename(input_path).split('.')[0]
        output_filename = f"{filename_base}_compressed.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, 'compressed', output_filename)
        
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'compressed'), exist_ok=True)
        
        # Ajustar CRF basado en la calidad pedida
        crf_map = {'high': '23', 'medium': '28', 'low': '32'}
        crf_value = crf_map.get(quality, '28')
        
        cmd = [
            ffmpeg_exe,
            '-y', # Overwrite
            '-i', input_path,
            '-vcodec', 'libx264',
            '-crf', crf_value,
            '-preset', 'fast',
            '-pix_fmt', 'yuv420p',  # Fix for Windows Media Player incompatibility
            '-acodec', 'aac',       # Ensure audio is compliant
            output_path
        ]
        
        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
        
        duration_s = 0
        duration_re = re.compile(r"Duration: (\d{2}:\d{2}:\d{2}\.\d{2})")
        time_re = re.compile(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})")
        
        # Leemos stderr linea por linea para obtener el progreso
        for line in process.stderr:
            # Capturar Duracion total
            if duration_s == 0:
                match_duration = duration_re.search(line)
                if match_duration:
                    duration_s = parse_time(match_duration.group(1))
            
            # Capturar tiempo actual
            match_time = time_re.search(line)
            if match_time and duration_s > 0:
                current_time_s = parse_time(match_time.group(1))
                percent = (current_time_s / duration_s) * 100
                
                # Actualizar base de datos masomenos cada iteración (optimizable en produccion)
                # Al ser SQLite / poco volumen esto esta bien para progreso en vivo.
                if percent > task.progress + 1.0: # Solo guardamos si subio de a 1%
                    task.progress = min(percent, 99.9)
                    task.save()
                    
        process.wait()
        
        if process.returncode == 0 and os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                task.compressed_file.save(output_filename, File(f), save=False)
            task.status = 'COMPLETED'
            task.progress = 100.0
            task.save()
            
            # Limpiar archivo original para ahorrar espacio, opcional.
            # os.remove(input_path)
            # os.remove(output_path)
        else:
            task.status = 'FAILED'
            task.error_message = f"Process exitted with code {process.returncode}"
            task.save()
            
    except Exception as e:
        try:
            task = VideoTask.objects.get(id=task_id)
            task.status = 'FAILED'
            task.error_message = str(e)
            task.save()
        except:
            pass
