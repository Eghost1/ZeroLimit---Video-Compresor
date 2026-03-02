import os
import glob
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import VideoTask
from django.core.files import File
from django_q.tasks import async_task

class UploadStartView(APIView):
    def post(self, request):
        task = VideoTask.objects.create(status='UPLOADING')
        
        # Determine file extension if provided
        filename = request.data.get('filename', 'video.mp4')
        
        # Create a directory for this task's chunks
        chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', str(task.id))
        os.makedirs(chunk_dir, exist_ok=True)
        
        return Response({
            'task_id': task.id,
            'message': 'Upload session started. Start sending chunks.'
        })

class UploadChunkView(APIView):
    def post(self, request, task_id):
        try:
            task = VideoTask.objects.get(id=task_id)
        except VideoTask.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)
            
        chunk_index = request.data.get('chunk_index')
        total_chunks = request.data.get('total_chunks')
        chunk_data = request.FILES.get('file')
        
        if chunk_index is None or chunk_data is None or total_chunks is None:
            return Response({'error': 'Missing chunk parameters'}, status=400)
            
        chunk_index = int(chunk_index)
        total_chunks = int(total_chunks)
        
        chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', str(task.id))
        chunk_path = os.path.join(chunk_dir, f"{chunk_index}.chunk")
        
        with open(chunk_path, 'wb') as f:
            for chunk in chunk_data.chunks():
                f.write(chunk)
                
        # Check if all chunks have been received
        uploaded_chunks = len(glob.glob(os.path.join(chunk_dir, '*.chunk')))
        if uploaded_chunks == total_chunks:
            # Reconstruct the original file
            final_filename = request.data.get('filename', 'video.mp4')
            final_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f"{task.id}_{final_filename}")
            
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'uploads'), exist_ok=True)
            
            with open(final_file_path, 'wb') as final_f:
                for i in range(total_chunks):
                    idx_path = os.path.join(chunk_dir, f"{i}.chunk")
                    if os.path.exists(idx_path):
                        with open(idx_path, 'rb') as chunk_f:
                            final_f.write(chunk_f.read())
                        os.remove(idx_path) # Clean up chunk
            
            # Remove chunk dir
            try:
                os.rmdir(chunk_dir)
            except:
                pass
                
            # Attach to model
            with open(final_file_path, 'rb') as f:
                task.original_file.save(f"{task.id}_{final_filename}", File(f), save=False)
            
            task.status = 'PENDING'
            task.save()
            
            # Start background compression task
            # We pass the compression quality parameters from the client if needed
            quality = request.data.get('quality', 'medium') 
            async_task('compressor.tasks.compress_video', task.id, quality)
            
            return Response({'message': 'Upload complete, processing started', 'status': 'PENDING'})
        
        return Response({
            'message': f'Chunk {chunk_index} received',
            'progress': (uploaded_chunks / total_chunks) * 100
        })

class TaskStatusView(APIView):
    def get(self, request, task_id):
        try:
            task = VideoTask.objects.get(id=task_id)
        except VideoTask.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)
            
        response_data = {
            'status': task.status,
            'progress': task.progress,
            'error_message': task.error_message
        }
        
        if task.status == 'COMPLETED' and task.compressed_file:
            response_data['download_url'] = task.compressed_file.url
            
        return Response(response_data)
