from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.files import File
from tempfile import NamedTemporaryFile
import base64
import speech_recognition as sr
import moviepy.editor as mp
from rest_framework.generics import RetrieveAPIView
from .models import Videos
from .serializers import VideoSerializer
from drf_yasg.utils import swagger_auto_schema
from django.http import  StreamingHttpResponse, FileResponse



class VideoDetail(RetrieveAPIView):
    queryset = Videos.objects.all()
    serializer_class = VideoSerializer
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary="Stream video",
        operation_description="This API endpoint streams an uploaded video.",
        responses={
            200: "OK",
            404: "Not Found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # Assuming you have a field in your serializer that contains the video file path
        video_path = instance.file.path

        try:
            # Open and stream the video file using StreamingHttpResponse
            with open(video_path, 'rb') as video_file:
                response = StreamingHttpResponse(video_file.read(), content_type='video/mp4')
                response['Content-Disposition'] = f'inline; filename="{instance.title}.mp4"'
                return response
        except FileNotFoundError:
            return Response(data={"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)




class UploadVideo(APIView):
    serializer_class = VideoSerializer
    temp_file = None

    @swagger_auto_schema(
    operation_summary = "Upload video",
    operation_description = "This is an api for uploading videos coming from the front end in bits and merging them",
    responses={
            201: VideoSerializer,  # Specify the serializer for the 201 (Created) response
            400: "Bad Request",
            500: "Internal Server Error",
        },

    
)

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the video_file from the request data
            video_file = request.data.get('video_file')

            # Ensure video_file is not None and is a valid base64-encoded string
            if video_file is None:
                return Response(data={"error": "video_file is missing"}, status=status.HTTP_400_BAD_REQUEST)

            video_file = base64.b64decode(video_file)

            is_last_chunk = request.data.get('is_last_chunk', False)

            if not self.temp_file:
                # Create a temporary file to store the video if it doesn't exist
                self.temp_file = NamedTemporaryFile(delete=False)
                self.temp_file.close()  # Close the temporary file initially

            # Append the video chunk to the temporary file
            with open(self.temp_file.name, 'ab') as file:
                file.write(video_file)

            if is_last_chunk:
                video_instance = self.finalize_video(request.data.get('title'))  # Finalize the video if it's the last chunk
                # Serialize the video object
                serializer = self.serializer_class(video_instance)

                # Return the serialized video object as a response
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def finalize_video(self, title):
        try:
            if self.temp_file:
                # Transcribe the video
                transcription = self.transcribe_video(self.temp_file.name)

                # Create a Video instance with the temporary file and transcription
                video_instance = Videos.objects.create(
                    title=title,
                    file=File(self.temp_file, name='video.mp4'),  # You can adjust the file name as needed
                    transcription=transcription  # Save the transcription
                )
                self.temp_file = None  # Reset the temporary file

        except Exception as e:
            return Response(data={"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def transcribe_video(self, video_path):
        recognizer = sr.Recognizer()
        transcription = ""

        try:
            # Convert the video's audio to WAV format
            video = mp.VideoFileClip(video_path)
            audio_path = video_path.replace('.mp4', '.wav')
            video.audio.write_audiofile(audio_path)

            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)  # Record the entire audio content
                transcription = recognizer.recognize_google(audio)  # Perform Google Web Speech API transcription

            # Clean up the temporary WAV audio file
            mp.os.remove(audio_path)
        except sr.UnknownValueError:
            transcription = "Transcription could not be generated"
        except sr.RequestError as e:
            transcription = f"Could not request results from Google Web Speech API; {e}"

        return transcription

