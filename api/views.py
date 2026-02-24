# simple test end points
# api/views.py
import base64
import io
import os
import requests
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, GeneratedImage, EditedImage, ImageScore, AuditLog, ForensicRequest
from .serializers import (
    UserSerializer, RegisterSerializer, GeneratedImageSerializer, EditedImageSerializer,
    ImageScoreSerializer, AuditLogSerializer, ForensicRequestSerializer
)
from django.conf import settings

COLAB_ML_URL = settings.COLAB_ML_URL

# Simple registration view
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

# Example: List generated images for user
class MyGeneratedImagesView(generics.ListAPIView):
    serializer_class = GeneratedImageSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return GeneratedImage.objects.filter(user=self.request.user).order_by('-created_at')

# Admin-only view example
class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.is_superuser:
            return AuditLog.objects.all().order_by('-timestamp')
        return AuditLog.objects.filter(user=user).order_by('-timestamp')

# Forensic request create
class ForensicRequestCreateView(generics.CreateAPIView):
    serializer_class = ForensicRequestSerializer
    permission_classes = (IsAuthenticated,)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Approve forensic request (admin only)
class ForensicApproveView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, pk):
        user = request.user
        if user.role != 'admin' and not user.is_superuser:
            return Response({'detail':'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            req = ForensicRequest.objects.get(pk=pk)
        except ForensicRequest.DoesNotExist:
            return Response({'detail':'Not found'}, status=status.HTTP_404_NOT_FOUND)
        req.is_approved = True
        req.approved_at = timezone.now()
        req.save()
        return Response({'detail':'approved'})

#     frontend – calls Colab ML service when COLAB_ML_URL is set
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_forensic_sketch(request):
    user = request.user

    if user.role != "forensic" and not user.is_superuser:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if not COLAB_ML_URL:
        return Response(
            {"error": "COLAB_ML_URL is not configured on the server"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    prompt = request.data.get("prompt")
    case_type = request.data.get("case_type", "criminal")
    age = request.data.get("age")

    if not prompt:
        return Response({"error": "prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

    if age is not None and age != "":
        try:
            age = int(age)
        except (TypeError, ValueError):
            return Response({"error": "age must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        age = None

    ml_url = COLAB_ML_URL if COLAB_ML_URL.endswith("/generate") else f"{COLAB_ML_URL.rstrip('/')}/generate"
    try:
        ml_resp = requests.post(
            ml_url,
            json={"prompt": prompt, "case_type": case_type, "age": age},
            headers={
                "ngrok-skip-browser-warning": "1",
                "User-Agent": "SmartSketch-Django/1.0",
            },
            timeout=120,
        )
    except requests.RequestException as e:
        return Response(
            {"error": f"Failed to reach ML service: {e}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    try:
        ml_data = ml_resp.json()
    except ValueError:
        snippet = (ml_resp.text or "")[:400]
        return Response(
            {
                "error": "Invalid JSON from ML service",
                "debug": {
                    "status_code": ml_resp.status_code,
                    "response_preview": snippet,
                },
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if ml_resp.status_code != 200 or not ml_data.get("success"):
        return Response(
            {
                "error": ml_data.get("error", "ML generation failed"),
                "metadata": ml_data.get("metadata", {}),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    image_b64 = ml_data.get("image_base64")
    if not image_b64:
        return Response(
            {"error": "ML service did not return image_base64"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        return Response(
            {"error": "Failed to decode image from ML service"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    generation_id = ml_data.get("generation_id") or "forensic"
    filename = f"{generation_id}.png"
    image_file = ContentFile(image_bytes, name=filename)

    generated = GeneratedImage.objects.create(
        user=user,
        prompt=prompt,
        image_file=image_file,
        seed=ml_data.get("metadata", {}).get("seed"),
        model_version=ml_data.get("metadata", {}).get("model_version", ""),
    )

    scores = ml_data.get("scores") or {}
    ImageScore.objects.create(
        image=generated,
        clip_score=scores.get("clip_score"),
        identity_score=scores.get("identity_score"),
        final_score=scores.get("combined_score"),
    )

    AuditLog.objects.create(
        user=user,
        action="generate",
        ip_address=request.META.get("REMOTE_ADDR"),
        prompt_used=prompt,
        image=generated,
    )

    return Response(
        {
            "id": generated.id,
            "image_url": request.build_absolute_uri(generated.image_file.url),
            "scores": scores,
            "metadata": ml_data.get("metadata", {}),
            "generation_id": generation_id,
        },
        status=status.HTTP_200_OK,
    )

