# api/serializers.py
from rest_framework import serializers
from .models import User, GeneratedImage, EditedImage, ImageScore, AuditLog, ForensicRequest
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','role','first_name','last_name')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ('username','email','password','role')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            role=validated_data.get('role', 'general'),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class GeneratedImageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = GeneratedImage
        fields = '__all__'

class EditedImageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = EditedImage
        fields = '__all__'

class ImageScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageScore
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class ForensicRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForensicRequest
        fields = '__all__'
