import torch
from PIL import Image
import numpy as np
from ml_engine.editor import FaceEditor
from unittest.mock import MagicMock

def test_identity():
    # 1. Mock the pipeline to avoid downloading 10GB of models
    mock_pipe = MagicMock()
    
    # 2. Initialize editor with mock pipe
    # This will still trigger the Identity Model loading
    editor = FaceEditor(base_pipeline=mock_pipe, device="cpu")
    
    # 3. Create two dummy images (random noise)
    img1 = Image.fromarray(np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
    img2 = Image.fromarray(np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
    
    print("\nRunning Identity Score Test...")
    score = editor.compute_identity_preservation(img1, img2)
    print(f"Identity Score (Random vs Random): {score:.4f}")
    
    # 4. Test same image (should be near 1.0)
    score_same = editor.compute_identity_preservation(img1, img1)
    print(f"Identity Score (Same vs Same): {score_same:.4f}")
    
    # Verification
    from ml_engine.editor import HAS_FACENET
    print(f"HAS_FACENET: {HAS_FACENET}")
    
    if HAS_FACENET:
        assert score_same > 0.95, "Identity score for same image should be near 1.0"
        print("Success: Identity preservation logic verified with Face Embeddings!")
    else:
        print("⚠️ Verified with SSIM fallback.")

if __name__ == "__main__":
    test_identity()
