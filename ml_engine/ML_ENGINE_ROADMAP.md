# SmartSketch ML Engine Roadmap & Technical Analysis

This document outlines the current technical status, identified issues, and future improvements for the SmartSketch ML Engine.

## 📊 Current Architecture
The ML Engine is a hybrid system combining:
- **LLM Validator:** Qwen-2.5 for prompt enhancement.
- **Image Generator:** SDXL 1.0 with LoRA support.
- **Image Editor:** SDXL Img2Img for attribute modification.
- **Sketch Converter:** ControlNet-Canny for photo-to-sketch transformation.

---

## 🛠️ Identified Technical Issues

### 1. Identity Preservation (Medium Priority)
- **Problem:** Current identity scoring uses SSIM (Structural Similarity). This measures pixel/texture similarity but fails to capture "facial identity" (e.g., bone structure, eye spacing).
- **Impact:** Edits may "drift" away from the original subject's appearance.
- **Proposed Solution:** Integrate a Facial Recognition model (e.g., **InsightFace** or **FaceNet**) to compare high-dimensional embeddings before and after edits.

### 2. Edit Precision (High Priority)
- **Problem:** `img2img` at high strengths often re-generates the entire face structure instead of just adding the requested attribute (e.g., adding a beard changes the jawline).
- **Impact:** Loss of forensic accuracy during iterative refinement.
- **Proposed Solution:** 
    - Implement **Semantic Inpainting** using automated segmentation masks (e.g., Segment Anything Model or MediaPipe).
    - Use **ControlNet (Depth/Canny)** to lock facial geometry while modifying textures.

### 3. Processing Latency (Critical Priority)
- **Problem:** API requests are synchronous. SDXL generation (20-30s) blocks the server and can lead to browser timeouts.
- **Impact:** Poor user experience and lack of scalability.
- **Proposed Solution:** Implement an asynchronous task queue using **Celery & Redis**. Provide `task_id` for polling or use WebSockets for real-time progress updates.

### 4. GPU Memory Management (Medium Priority)
- **Status:** COMPLETED ✅
- **Implementation:** 
    - Added `LOW_VRAM_MODE` global toggle in `.env`.
    - Integrated `enable_model_cpu_offload()` across all pipelines.
    - Enabled `vae_slicing()` and `vae_tiling()` to handle 1024x1024 images on low VRAM.
    - Added memory sharing logic in `SmartSketchPipeline`.

---

## 🚀 Future Feature Roadmap

### 1. Conversational Context (LLM Memory)
Currently, the LLM validator is stateless. It should be updated to receive the **Conversation History** so it can handle relative prompts like *"make his eyes a bit darker"* without losing previously established features.

### 2. Sketch-to-Photo Realization
Implement a reverse pipeline that takes a hand-drawn forensic sketch and uses **ControlNet-Scribble** to generate a photorealistic "suspect photo."

### 3. Forensic Guardrails & Integrity
- **Safety Checker:** Prevent generation of public figures or non-consensual imagery.
- **Forensic Watermarking:** Embed invisible watermarks (e.g., SteganoGAN) to identify images as AI-generated for legal accountability.

### 4. Attribute Sliders (Latent Directions)
Move beyond pure text prompts by implementing UI sliders for deterministic attributes:
- Age (Young -> Old)
- Masculinity / Femininity
- Facial Weight
- Expression Intensity (Neutral -> Smiling)

---
*Last Updated: 2026-04-19*
