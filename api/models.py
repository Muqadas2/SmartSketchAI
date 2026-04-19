# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('forensic', 'Forensic User'),
        ('editor', 'Attribute Editor'),
        ('general', 'General User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='general')
    email_verified = models.BooleanField(default=False)
    # optionally add profile fields
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

class GeneratedImage(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='generated_images', null=True, blank=True)
    prompt = models.TextField()
    image_file = models.ImageField(upload_to='generated/', null=True, blank=True)
    seed = models.BigIntegerField(null=True, blank=True)
    model_version = models.CharField(max_length=50, blank=True)
    forensic_hash = models.CharField(max_length=64, blank=True, null=True, help_text="SHA-256 hash of the pixel data")
    is_watermarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GeneratedImage {self.id} by {self.user.username}"

class EditedImage(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='edited_images', null=True, blank=True)
    original_image = models.ForeignKey(GeneratedImage, on_delete=models.CASCADE, related_name='edits', null=True, blank=True)
    edit_prompt = models.TextField()
    edited_file = models.ImageField(upload_to='edited/')
    forensic_hash = models.CharField(max_length=64, blank=True, null=True, help_text="SHA-256 hash of the pixel data")
    is_watermarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ImageScore(models.Model):
    image = models.ForeignKey(GeneratedImage, on_delete=models.CASCADE, null=True, blank=True)
    edited_image = models.ForeignKey(EditedImage, on_delete=models.CASCADE, null=True, blank=True)
    clip_score = models.FloatField(null=True, blank=True)
    identity_score = models.FloatField(null=True, blank=True)
    final_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    ACTIONS = (
        ('generate', 'Generate'),
        ('edit', 'Edit'),
        ('view', 'View'),
        ('login', 'Login'),
    )
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTIONS)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    prompt_used = models.TextField(null=True, blank=True)
    image = models.ForeignKey(GeneratedImage, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ForensicRequest(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    reason = models.TextField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)


