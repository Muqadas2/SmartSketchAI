import torch
from django.conf import settings
from ml_engine.pipeline import SmartSketchPipeline

class MLService:
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        # Check if local ML is enabled in settings
        ml_config = getattr(settings, 'ML_CONFIG', {})
        if not ml_config.get('USE_LOCAL_ML', False):
            raise RuntimeError("Local ML Engine is disabled in settings (USE_LOCAL_ML=False).")

        if cls._pipeline is None:
            print("🚀 Initializing SmartSketch Pipeline...")
            
            device = ml_config.get('DEVICE', 'cuda' if torch.cuda.is_available() else 'cpu')
            lora_path = ml_config.get('LORA_PATH', None)
            
            import os
            if lora_path and not os.path.exists(lora_path):
                print(f"⚠️ LoRA weights not found at {lora_path}, loading without LoRA.")
                lora_path = None

            cls._pipeline = SmartSketchPipeline.from_pretrained(
                lora_path=lora_path,
                validator_model=ml_config.get('VALIDATOR_MODEL', "Qwen/Qwen2.5-3B-Instruct"),
                sdxl_model=ml_config.get('SDXL_MODEL', "stabilityai/stable-diffusion-xl-base-1.0"),
                lora_strength=ml_config.get('LORA_STRENGTH', 0.3),
                device=device,
                enable_sketch=ml_config.get('ENABLE_SKETCH', True),
                enable_editing=ml_config.get('ENABLE_EDITING', True)
            )
            print("✅ Pipeline initialized successfully.")
        return cls._pipeline
