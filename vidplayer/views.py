from django.http import FileResponse
from django.views.generic import DetailView
from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from .models import Videos
from .serializers import VideoSerializer

# Create your views here.

class VideoView(generics.GenericAPIView):
    queryset = Videos.objects.all()
    serializer_class = VideoSerializer

    def post(self, request, *args, **kwargs):

        # Deserialize the request data using the serializer

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            # Save the video to the database

            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=self.queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)



class ViewVideo(DetailView):
    model = Videos
    context_object_name = 'video'

    def render_to_response(self, context, **response_kwargs):
        video = self.get_object()
        video_file = video.video

        response = FileResponse(video_file.open('rb'))
        response['Content-Type'] = 'video/mp4'  
        response['Content-Disposition'] = 'inline'  
        return response




