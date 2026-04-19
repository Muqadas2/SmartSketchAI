import torch
from diffusers import StableDiffusionXLInpaintPipeline
from PIL import Image
from typing import Optional, Dict
import random
from datetime import datetime
from .masker import FaceMasker

class FaceInpainter:
    """
    Precision semantic editing using SDXL Inpainting
    """
    def __init__(
        self,
        base_pipeline=None,
        device: str = "cuda",
        enable_offload: bool = False
    ):
        print("[Inpainter] Loading Face Inpainter...")
        self.device = device
        self.masker = FaceMasker()
        
        # Reuse existing SDXL components to save VRAM
        if base_pipeline:
            print("  - Reusing SDXL components from generator...")
            self.pipe = StableDiffusionXLInpaintPipeline(
                vae=base_pipeline.vae,
                text_encoder=base_pipeline.text_encoder,
                text_encoder_2=base_pipeline.text_encoder_2,
                tokenizer=base_pipeline.tokenizer,
                tokenizer_2=base_pipeline.tokenizer_2,
                unet=base_pipeline.unet,
                scheduler=base_pipeline.scheduler
            )
        else:
            print("  - Loading new SDXL Inpaint pipeline...")
            self.pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            
        if enable_offload and device == "cuda":
            print("  - Enabling Model CPU Offload for Inpainter")
            self.pipe.enable_model_cpu_offload()
            self.pipe.enable_vae_slicing()
            self.pipe.enable_vae_tiling()
        else:
            self.pipe.to(device)
            
        print("✅ Face Inpainter ready!")

    def inpaint_edit(
        self,
        image: Image.Image,
        prompt: str,
        target_region: Optional[str] = None,
        strength: float = 0.75,
        num_inference_steps: int = 30,
        seed: Optional[int] = None
    ) -> Dict:
        """
        Edit a specific region of the face
        """
        # Auto-detect region if not provided
        if not target_region:
            target_region = self.masker.detect_region_from_prompt(prompt)
            
        print(f"\n[Inpainter] Target Region: {target_region}")
        
        # Create mask
        mask = self.masker.create_mask(image, target_region)
        
        if mask is None:
            return {
                'success': False,
                'error': f"Could not generate mask for region: {target_region}"
            }
            
        # Set up generator for reproducibility
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
            
        # Build prompt
        full_prompt = f"professional forensic photograph, {prompt}, realistic, detailed facial features"
        negative_prompt = "low quality, blurry, distorted, anime, cartoon, sketch, painting"
        
        try:
            print(f"🎨 Applying inpaint to {target_region}...")
            result_image = self.pipe(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                image=image,
                mask_image=mask,
                strength=strength,
                num_inference_steps=num_inference_steps,
                generator=generator
            ).images[0]
            
            return {
                'success': True,
                'edited_image': result_image,
                'mask': mask,
                'target_region': target_region
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Inpaint failed: {str(e)}"
            }
