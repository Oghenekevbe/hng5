from django.urls import path
from .views import VideoView, ViewVideo  

urlpatterns = [
    path("video_api/", VideoView.as_view(), name="video_api"),
    path("<slug:slug>/", ViewVideo.as_view(), name="video"),
]
