import uuid
from django.db import models

class VideoTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    compressed_file = models.FileField(upload_to='compressed/', null=True, blank=True)
    status = models.CharField(max_length=50, default='UPLOADING') # UPLOADING, PENDING, PROCESSING, COMPLETED, FAILED
    progress = models.FloatField(default=0.0) # 0 to 100
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} - {self.status}"
