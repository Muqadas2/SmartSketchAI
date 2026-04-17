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
from .ml_service import MLService
from django.conf import settings

COLAB_ML_URL = settings.COLAB_ML_URL

def pil_to_content_file(image, filename):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=filename)

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_forensic_sketch(request):
    user = request.user

    if user.role != "forensic" and not user.is_superuser:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    prompt = request.data.get("prompt")
    case_type = request.data.get("case_type", "criminal")
    age = request.data.get("age")
    output_type = request.data.get("output_type", "photo")

    if not prompt:
        return Response({"error": "prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

    if age is not None and age != "":
        try:
            age = int(age)
        except (TypeError, ValueError):
            return Response({"error": "age must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        age = 30  # Default age

    # ================================================================
    # 1. Try Colab ML Service First (Primary)
    # ================================================================
    if COLAB_ML_URL:
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
            
            if ml_resp.status_code == 200:
                ml_data = ml_resp.json()
                if ml_data.get("success"):
                    image_b64 = ml_data.get("image_base64")
                    if image_b64:
                        image_bytes = base64.b64decode(image_b64)
                        generation_id = ml_data.get("generation_id") or "forensic"
                        image_file = ContentFile(image_bytes, name=f"{generation_id}.png")

                        generated = GeneratedImage.objects.create(
                            user=user,
                            prompt=prompt,
                            image_file=image_file,
                            seed=ml_data.get("metadata", {}).get("seed"),
                            model_version=ml_data.get("metadata", {}).get("model_version", "colab-v1"),
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
                                "provider": "colab"
                            },
                            status=status.HTTP_200_OK,
                        )
            print(f"⚠️ Colab ML service returned status {ml_resp.status_code}")
        except Exception as colab_e:
            print(f"⚠️ Colab ML service failed: {colab_e}")

    # ================================================================
    # 2. Try Local ML Engine as Fallback (if enabled)
    # ================================================================
    ml_config = getattr(settings, 'ML_CONFIG', {})
    if ml_config.get('USE_LOCAL_ML', False):
        try:
            pipeline = MLService.get_pipeline()
            ml_data = pipeline.generate_sketch(
                prompt=prompt,
                case_type=case_type,
                age=age,
                output_type=output_type
            )
            
            if ml_data.get("success"):
                final_image = ml_data.get("image")
                generation_id = ml_data.get("generation_id")
                image_file = pil_to_content_file(final_image, f"{generation_id}.png")

                generated = GeneratedImage.objects.create(
                    user=user,
                    prompt=prompt,
                    image_file=image_file,
                    seed=ml_data.get("metadata", {}).get("seed"),
                    model_version=ml_data.get("metadata", {}).get("model_version", "local-v1"),
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
                        "provider": "local"
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as local_e:
            print(f"⚠️ Local ML Engine failed: {local_e}")

    return Response(
        {"error": "ML generation failed. Colab service unavailable and local ML disabled/failed."},
        status=status.HTTP_503_SERVICE_UNAVAILABLE
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_forensic_sketch(request):
    user = request.user

    if user.role != "forensic" and not user.is_superuser:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    original_image_id = request.data.get("original_image_id")
    edit_prompt = request.data.get("edit_prompt")
    strength = request.data.get("strength", 0.6)

    if not original_image_id or not edit_prompt:
        return Response({"error": "original_image_id and edit_prompt are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        strength = float(strength)
    except (TypeError, ValueError):
        return Response({"error": "strength must be a float"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        generated_image = GeneratedImage.objects.get(pk=original_image_id, user=user)
    except GeneratedImage.DoesNotExist:
        return Response({"error": "Original image not found"}, status=status.HTTP_404_NOT_FOUND)

    # ================================================================
    # 1. Try Colab ML Service First (Primary)
    # ================================================================
    if COLAB_ML_URL:
        ml_url = COLAB_ML_URL.rstrip('/').replace('/generate', '') + '/edit'
        try:
            with generated_image.image_file.open('rb') as f:
                original_image_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            ml_resp = requests.post(
                ml_url,
                json={
                    "generation_id": f"gen_{generated_image.id}",
                    "original_image": original_image_b64,
                    "edit_prompt": edit_prompt,
                    "strength": strength,
                },
                headers={
                    "ngrok-skip-browser-warning": "1",
                    "User-Agent": "SmartSketch-Django/1.0",
                },
                timeout=120,
            )
            
            if ml_resp.status_code == 200:
                ml_data = ml_resp.json()
                if ml_data.get("success"):
                    edited_image_b64 = ml_data.get("edited_image")
                    if edited_image_b64:
                        edited_bytes = base64.b64decode(edited_image_b64)
                        edit_id = ml_data.get("edit_id") or f"edit_{generated_image.id}"
                        edited_file = ContentFile(edited_bytes, name=f"{edit_id}.png")

                        edited = EditedImage.objects.create(
                            user=user,
                            original_image=generated_image,
                            edit_prompt=edit_prompt,
                            edited_file=edited_file,
                        )

                        scores = ml_data.get("scores") or {}
                        identity_score = ml_data.get("identity_score", 0)

                        ImageScore.objects.create(
                            edited_image=edited,
                            clip_score=scores.get("clip_score"),
                            identity_score=identity_score,
                            final_score=scores.get("combined_score"),
                        )

                        AuditLog.objects.create(
                            user=user,
                            action="edit",
                            ip_address=request.META.get("REMOTE_ADDR"),
                            prompt_used=edit_prompt,
                            image=generated_image,
                        )

                        return Response(
                            {
                                "id": edited.id,
                                "original_image_id": generated_image.id,
                                "edited_image_url": request.build_absolute_uri(edited.edited_file.url),
                                "edit_prompt": edit_prompt,
                                "identity_score": identity_score,
                                "provider": "colab"
                            },
                            status=status.HTTP_200_OK,
                        )
        except Exception as colab_e:
            print(f"⚠️ Colab ML edit failed: {colab_e}")

    # ================================================================
    # 2. Try Local ML Engine as Fallback (if enabled)
    # ================================================================
    ml_config = getattr(settings, 'ML_CONFIG', {})
    if ml_config.get('USE_LOCAL_ML', False):
        try:
            from PIL import Image
            with generated_image.image_file.open('rb') as f:
                pil_image = Image.open(f).convert('RGB')

            pipeline = MLService.get_pipeline()
            ml_data = pipeline.edit_sketch(
                generation_id=str(generated_image.id),
                original_image=pil_image,
                edit_prompt=edit_prompt,
                strength=strength
            )

            if ml_data.get("success"):
                edited_pil = ml_data.get("edited_image")
                edit_id = ml_data.get("edit_id")
                edited_file = pil_to_content_file(edited_pil, f"{edit_id}.png")

                edited = EditedImage.objects.create(
                    user=user,
                    original_image=generated_image,
                    edit_prompt=edit_prompt,
                    edited_file=edited_file,
                )

                scores = ml_data.get("scores") or {}
                identity_score = ml_data.get("identity_score", 0)

                ImageScore.objects.create(
                    edited_image=edited,
                    clip_score=scores.get("clip_score"),
                    identity_score=identity_score,
                    final_score=scores.get("combined_score"),
                )

                AuditLog.objects.create(
                    user=user,
                    action="edit",
                    ip_address=request.META.get("REMOTE_ADDR"),
                    prompt_used=edit_prompt,
                    image=generated_image,
                )

                return Response(
                    {
                        "id": edited.id,
                        "original_image_id": generated_image.id,
                        "edited_image_url": request.build_absolute_uri(edited.edited_file.url),
                        "edit_prompt": edit_prompt,
                        "identity_score": identity_score,
                        "provider": "local"
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as local_e:
            print(f"⚠️ Local ML edit failed: {local_e}")

    return Response(
        {"error": "ML edit failed. Colab service unavailable and local ML disabled/failed."},
        status=status.HTTP_503_SERVICE_UNAVAILABLE
    )
