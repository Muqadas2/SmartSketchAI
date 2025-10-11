from rest_framework import serializers
from .models import TrainingJob, GeneratedImage

class TrainingJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingJob
        fields = '__all__'  # include all fields

class GeneratedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = '__all__'
