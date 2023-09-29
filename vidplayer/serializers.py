from rest_framework import serializers
from .models import Videos

class VideoSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    video = serializers.FileField()
    class Meta:
        
        model = Videos
        fields = ['title', 'video']