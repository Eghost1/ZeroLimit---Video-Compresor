from django.urls import path
from .views import UploadStartView, UploadChunkView, TaskStatusView

urlpatterns = [
    path('upload/start/', UploadStartView.as_view(), name='upload-start'),
    path('upload/chunk/<uuid:task_id>/', UploadChunkView.as_view(), name='upload-chunk'),
    path('status/<uuid:task_id>/', TaskStatusView.as_view(), name='task-status'),
]
