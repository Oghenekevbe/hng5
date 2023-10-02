from rest_framework import serializers
from .models import Videos


class VideoSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    file = serializers.FileField()
    transcription = serializers.CharField()

    class Meta:
        
        model = Videos
        fields = ['title', 'file', 'transcription']