# PROJECT REPORT 02
# Consistent AI Influencer Image Generation Pipeline
### ComfyUI · Stable Diffusion XL · IP-Adapter · ControlNet · LoRA Training

---

**Document Version:** 1.0.0
**Classification:** Technical Design & Implementation Report
**Prepared By:** Senior Systems Architect
**Date:** 2026-03-20
**Status:** Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Requirements](#system-requirements)
3. [Architecture Overview](#architecture-overview)
4. [Component Deep Dive](#component-deep-dive)
5. [Environment Setup & Configuration](#environment-setup--configuration)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [LoRA Training for Facial Consistency](#lora-training-for-facial-consistency)
8. [ComfyUI API Integration](#comfyui-api-integration)
9. [Testing & Validation](#testing--validation)
10. [Quality Control Standards](#quality-control-standards)

---

## 1. Executive Summary

The AI Influencer Image Generation Pipeline is the visual identity engine of the content automation system. Its singular challenge — and primary engineering objective — is producing **photorealistic, character-consistent images** across unlimited variations of pose, outfit, lighting, and setting, without a real human model.

This is achieved through a multi-technique consistency stack:

1. **Character LoRA** — A fine-tuned Stable Diffusion model trained on 20-30 images of the character's face, baking identity into model weights.
2. **IP-Adapter** — An image conditioning layer that takes a reference face image as a "visual prompt," enforcing identity even on novel prompts.
3. **ControlNet** — A structural control layer that enforces exact body poses, preventing anatomical deformations.
4. **ComfyUI** — A node-based workflow UI and API server that orchestrates the full multi-model inference pipeline in a single JSON workflow definition.

The pipeline accepts a **text prompt** and a **reference face image** as input, and returns a **1024x1024 JPEG** image as output via a REST API.

---

## 2. System Requirements

### 2.1 Hardware Requirements

> **CRITICAL NOTE:** Image generation is GPU-bound. CPU inference is 50-200x slower and not practical for production use.

| Component | Minimum (Testing) | Recommended (Production) |
|-----------|-------------------|--------------------------|
| GPU | NVIDIA RTX 3060 12GB VRAM | NVIDIA RTX 4090 24GB VRAM |
| CPU | 8-core | 16-core |
| RAM | 32 GB | 64 GB |
| Storage | 100 GB SSD | 1 TB NVMe SSD |
| OS | Ubuntu 22.04 | Ubuntu 22.04 LTS |
| CUDA | 12.1+ | 12.4+ |
| cuDNN | 8.9+ | 9.x |

**Cloud GPU Alternative (if no local GPU):**
- RunPod.io — RTX 4090 from $0.44/hr (Secure Cloud for persistent volumes)
- Vast.ai — Budget GPU rental

### 2.2 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11.x | ComfyUI runtime |
| PyTorch | 2.3.x (CUDA 12.1) | GPU inference backend |
| ComfyUI | Latest (git) | Workflow engine & API server |
| ComfyUI-Manager | Latest | Extension/node manager |
| xformers | 0.0.26+ | Memory-efficient attention |
| Kohya_ss | Latest | LoRA training framework |

### 2.3 Required Model Files

| Model | File Size | Source | Purpose |
|-------|-----------|--------|---------|
| RealVisXL V4.0 | 6.7 GB | CivitAI | Photorealism SDXL checkpoint |
| IP-Adapter SDXL ViT-H | 2.5 GB | HuggingFace | Face identity conditioning |
| ControlNet OpenPose SDXL | 1.5 GB | HuggingFace | Pose control |
| CLIP Vision ViT-H | 2.5 GB | HuggingFace | IP-Adapter vision encoder |
| VAE (SDXL) | 335 MB | HuggingFace | Latent-to-pixel decoder |
| **Character LoRA** | 50-200 MB | **Self-trained** | Your influencer's face identity |

**Total disk space required:** ~30 GB (models) + 1 GB (software) + variable (outputs)

---

## 3. Architecture Overview

### 3.1 System Diagram

```
                    +---------------------------+
                    |   Orchestration Engine    |
                    |  (Report 01 - FastAPI)    |
                    +------------+--------------+
                                 |  POST /generate
                                 |  { "prompt": "...", "pose_ref": "..." }
                                 v
+----------------------------------------------------------------+
|                     ComfyUI API Server                         |
|                     (port 8188)                                |
|                                                                |
|  +----------+   +-----------+   +---------------------------+ |
|  | CLIP Text|   | IP-Adapter|   |       ControlNet          | |
|  |  Encode  |   |  (Face    |   |  (OpenPose / Canny)       | |
|  | (prompt) |   |  Ref Img) |   |  (pose_reference_image)   | |
|  +----+-----+   +-----+-----+   +-------+-------------------+ |
|       |               |                 |                     |
|       +---------------+-----------------+                     |
|                        |                                      |
|                        v                                      |
|        +---------------------------------+                    |
|        |  KSampler (Base SDXL + LoRA)   |                    |
|        |  Steps: 30  CFG: 7  Denoise: 1 |                    |
|        +-----------------+--------------+                     |
|                          |                                    |
|                          v                                    |
|        +---------------------------------+                    |
|        |  KSampler Refiner Pass         |                    |
|        |  Steps: 10  Denoise: 0.35      |                    |
|        +-----------------+--------------+                     |
|                          |                                    |
|                          v                                    |
|        +---------------------------------+                    |
|        |  VAE Decode -> Save Image      |                    |
|        |  1024x1024 PNG/JPEG            |                    |
|        +-----------------+--------------+                     |
+---------------------------+------------------------------------+
                            |
                            v
                  +------------------+
                  |  Output Image    |
                  |  /outputs/*.jpg  |
                  +------------------+
```

### 3.2 Multi-Pass Consistency Stack

```
Pass 1: Base Composition
  Input:  [text_prompt + negative_prompt + LoRA weights + IP-Adapter face]
  Output: 1024x1024 latent (strong identity, composition, lighting)

Pass 2: Structural Control (optional - for specific poses)
  Input:  [pose_image -> OpenPose preprocessor -> ControlNet conditioning]
  Merged with Pass 1 via Combine Conditioning node

Pass 3: Refiner Pass
  Input:  [latent from Pass 1] + [refiner model CLIP]
  Output: High-detail 1024x1024 latent (skin texture, hair strands, eyes)

Pass 4: VAE Decode
  Input:  [final latent]
  Output: Pixel-space JPEG
```

---

## 4. Component Deep Dive

### 4.1 IP-Adapter — Why It's Critical

IP-Adapter encodes a reference face image into the same embedding space as text, then injects it as additional conditioning into the cross-attention layers of SDXL. The model simultaneously attends to both your text prompt AND the face image, maintaining identity without any LoRA or fine-tuning.

**Key parameters:**
- `weight` (0.0-1.5): Higher = stronger face adherence. Optimal: `0.7-0.9`
- Use **IP-Adapter ViT-H** for faces (higher fidelity than ViT-L)

### 4.2 ControlNet — Pose Injection

ControlNet conditions the denoising process on a structural signal (pose skeleton, edge map, depth map). OpenPose ControlNet is used to enforce specific body positions.

**Workflow:** `reference_pose_photo -> DWPose Preprocessor -> OpenPose ControlNet -> KSampler conditioning`

**Key parameters:**
- `strength`: 0.6-0.85 (lower = more creative freedom)
- `start_percent`: 0.0 (apply from the beginning)
- `end_percent`: 0.65 (stop after 65% of steps to allow feature generation)

### 4.3 Character LoRA — The Identity Anchor

A LoRA (Low-Rank Adaptation) is a tiny neural network adapter trained on top of SDXL. Trained on 20-30 images of a specific face, it learns to reproduce that face at will when triggered by a specific keyword.

**Training dataset:** 20-30 images minimum, 50-80 recommended
**Training steps:** 1500-2500 steps
**Output:** A `.safetensors` file (50-200 MB)
**Usage:** Load alongside SDXL, apply weight of 0.8-1.0, include trigger word in prompt

---

## 5. Environment Setup & Configuration

### 5.1 Install CUDA & System Dependencies

```bash
# Ubuntu 22.04
sudo apt update && sudo apt install -y git python3.11 python3.11-venv python3-pip \
    build-essential libgl1-mesa-glx libglib2.0-0 wget curl

# Install CUDA 12.4
wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda_12.4.0_550.54.14_linux.run
sudo sh cuda_12.4.0_550.54.14_linux.run --silent --toolkit

echo 'export PATH=/usr/local/cuda-12.4/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 5.2 Install ComfyUI

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

python3.11 -m venv venv
source venv/bin/activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
pip install xformers
```

### 5.3 Install ComfyUI Custom Nodes

```bash
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git

cd ComfyUI_IPAdapter_plus && pip install -r requirements.txt && cd ..
cd comfyui_controlnet_aux && pip install -r requirements.txt && cd ..
```

### 5.4 Download Models

```bash
MODEL_DIR="/path/to/ComfyUI/models"

# RealVisXL V4 photorealism checkpoint
wget -O "$MODEL_DIR/checkpoints/realvisxlV40.safetensors" \
  "https://civitai.com/api/download/models/361593?type=Model&format=SafeTensor"

# IP-Adapter SDXL
mkdir -p "$MODEL_DIR/ipadapter"
wget -O "$MODEL_DIR/ipadapter/ip-adapter_sdxl_vit-h.safetensors" \
  "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors"

# ControlNet OpenPose SDXL
mkdir -p "$MODEL_DIR/controlnet"
wget -O "$MODEL_DIR/controlnet/controlnet-openpose-sdxl.safetensors" \
  "https://huggingface.co/thibaud/controlnet-openpose-sdxl-1.0/resolve/main/OpenPoseXL2.safetensors"
```

### 5.5 Directory Structure

```
ComfyUI/
+-- models/
|   +-- checkpoints/
|   |   +-- realvisxlV40.safetensors
|   +-- ipadapter/
|   |   +-- ip-adapter_sdxl_vit-h.safetensors
|   +-- clip_vision/
|   |   +-- CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
|   +-- controlnet/
|   |   +-- controlnet-openpose-sdxl.safetensors
|   +-- loras/
|   |   +-- influencer_character_v1.safetensors   <- Your trained LoRA
|   +-- vae/
|       +-- sdxl_vae.safetensors
+-- custom_nodes/
|   +-- ComfyUI_IPAdapter_plus/
|   +-- comfyui_controlnet_aux/
+-- input/
|   +-- face_reference.jpg                        <- Character reference face
+-- output/
+-- workflows/
    +-- influencer_generation.json                <- Saved workflow
```

### 5.6 Launch ComfyUI Server

```bash
# Launch with API enabled (critical for automation)
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header

# For smaller GPUs (8-12 GB VRAM)
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header --lowvram --bf16-unet
```

---

## 6. Step-by-Step Implementation

### Step 1 — Build the ComfyUI Workflow (GUI)

1. Open `http://localhost:8188` in your browser
2. Clear the default workflow (Ctrl+D)
3. Build the following node graph:

```
[Load Checkpoint: realvisxlV40] --------------------------------+
                                                               |
[Load LoRA: influencer_v1, weight=0.9] <- applies to ckpt ----+
                                                               |
[CLIP Text Encode (+)] <- "photo of [TRIGGER_WORD], ..."      |
[CLIP Text Encode (-)] <- "ugly, deformed, cartoon, ..."      +---> [KSampler Base]
                                                               |     steps=30, cfg=7
[Load Image: face_reference.jpg]                              |     sampler=dpmpp_2m
    +---> [IPAdapterFaceID]                                   |     scheduler=karras
          weight=0.85 ----------------------------------------+
                                                               |
[Load Image: pose_reference.jpg]                              |
    +---> [DWPose Preprocessor]                               |
          +---> [Apply ControlNet: openpose] strength=0.7 ----+
                start=0.0, end=0.65

[KSampler Base] ---> [KSampler Refiner] ---> [VAE Decode] ---> [Save Image]
                      steps=10                                  output/
                      denoise=0.35
```

4. Save: **Workflow > Export (API format)** -> `workflows/influencer_generation.json`

### Step 2 — Create the API Integration Layer

```python
# image_api/generator.py
import asyncio
import json
import uuid
import httpx
from pathlib import Path
from typing import Optional

COMFY_URL = "http://localhost:8188"
WORKFLOW_PATH = Path("ComfyUI/workflows/influencer_generation.json")


async def generate_influencer_image(
    prompt: str,
    negative_prompt: str = "ugly, deformed, blurry, watermark, cartoon, anime",
    pose_image_path: Optional[str] = None,
    lora_weight: float = 0.9,
    ip_adapter_weight: float = 0.85,
    seed: int = -1
) -> bytes:
    """Generate a consistent influencer image via ComfyUI API. Returns raw JPEG bytes."""
    workflow = json.loads(WORKFLOW_PATH.read_text())
    client_id = str(uuid.uuid4())

    _inject_prompt(workflow, prompt, negative_prompt)
    _inject_lora_weight(workflow, lora_weight)
    _inject_ip_adapter_weight(workflow, ip_adapter_weight)
    _inject_seed(workflow, seed)

    if pose_image_path:
        await _upload_image(pose_image_path, "pose_reference.jpg")
        _inject_pose_image(workflow, "pose_reference.jpg")

    async with httpx.AsyncClient(timeout=300) as client:
        queue_resp = await client.post(
            f"{COMFY_URL}/prompt",
            json={"prompt": workflow, "client_id": client_id}
        )
        prompt_id = queue_resp.json()["prompt_id"]
        return await _poll_for_result(client, prompt_id)


async def _poll_for_result(client: httpx.AsyncClient, prompt_id: str) -> bytes:
    """Poll ComfyUI history until generation is complete."""
    for _ in range(120):  # 10 minute timeout
        await asyncio.sleep(5)
        history = (await client.get(f"{COMFY_URL}/history/{prompt_id}")).json()

        if prompt_id not in history:
            continue

        for node_output in history[prompt_id]["outputs"].values():
            if "images" in node_output:
                info = node_output["images"][0]
                img_resp = await client.get(
                    f"{COMFY_URL}/view",
                    params={"filename": info["filename"], "subfolder": info["subfolder"]}
                )
                return img_resp.content

    raise TimeoutError(f"Generation timed out for prompt_id={prompt_id}")


async def _upload_image(local_path: str, upload_name: str):
    async with httpx.AsyncClient() as client:
        with open(local_path, "rb") as f:
            await client.post(f"{COMFY_URL}/upload/image",
                              files={"image": (upload_name, f, "image/jpeg")})


def _inject_prompt(workflow: dict, positive: str, negative: str):
    for node in workflow.values():
        if node.get("class_type") == "CLIPTextEncode":
            title = node.get("_meta", {}).get("title", "").lower()
            if "positive" in title:
                node["inputs"]["text"] = positive
            elif "negative" in title:
                node["inputs"]["text"] = negative


def _inject_lora_weight(workflow: dict, weight: float):
    for node in workflow.values():
        if node.get("class_type") == "LoraLoader":
            node["inputs"]["strength_model"] = weight
            node["inputs"]["strength_clip"] = weight


def _inject_ip_adapter_weight(workflow: dict, weight: float):
    for node in workflow.values():
        if node.get("class_type") in ["IPAdapterFaceID", "IPAdapter"]:
            node["inputs"]["weight"] = weight


def _inject_seed(workflow: dict, seed: int):
    import random
    actual_seed = random.randint(0, 2**32) if seed == -1 else seed
    for node in workflow.values():
        if node.get("class_type") == "KSampler":
            node["inputs"]["seed"] = actual_seed
            break


def _inject_pose_image(workflow: dict, filename: str):
    for node in workflow.values():
        if node.get("class_type") == "LoadImage":
            if "pose" in node.get("_meta", {}).get("title", "").lower():
                node["inputs"]["image"] = filename
```

### Step 3 — Expose as a Microservice

```python
# image_api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from generator import generate_influencer_image

app = FastAPI(title="Image Generation Service")

class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = "ugly, deformed, blurry, watermark, cartoon"
    pose_image_path: Optional[str] = None
    lora_weight: float = 0.9
    ip_adapter_weight: float = 0.85
    seed: int = -1

@app.post("/generate", response_class=Response)
async def generate(request: GenerateRequest):
    try:
        image_bytes = await generate_influencer_image(**request.model_dump())
        return Response(content=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## 7. LoRA Training for Facial Consistency

### Step 1 — Prepare Training Dataset

```
training_data/
+-- influencer_v1/
    +-- 10_InfluencerName/       # "10" = repeat count, matches trigger word
    |   +-- img_001.jpg          # Close-up face, neutral expression
    |   +-- img_002.jpg          # 3/4 angle, smiling
    |   +-- img_003.jpg          # Side profile
    |   +-- img_004.jpg          # Different outfit (same face)
    |   +-- ... (20-50 total images)
    +-- regularization/          # Class regularization images
        +-- person/
            +-- (100 random "person" images from LAION dataset)
```

**Dataset quality requirements:**
- Resolution: minimum 512x512, ideal 1024x1024
- Consistent face, varied backgrounds and lighting
- No other faces in the frame
- No heavy makeup or extreme expressions in most images

### Step 2 — Install Kohya_ss

```bash
git clone https://github.com/bmaltais/kohya_ss.git
cd kohya_ss
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python kohya_gui.py
# Open http://localhost:7860
```

### Step 3 — Training Configuration (Dreambooth LoRA for SDXL)

| Parameter | Value | Reason |
|-----------|-------|--------|
| Base Model | RealVisXL V4.0 | Same model used at inference time |
| Training Type | SDXL LoRA | Matches target model architecture |
| Instance Prompt | `photo of InfluencerName person` | Trigger word for character |
| Class Prompt | `photo of a person` | Regularization anchor |
| Repeats | 10 | Amplify small dataset |
| Max Steps | 2000 | Sweet spot — prevents overfitting |
| Learning Rate | `1e-4` | Standard LoRA LR |
| Network Rank | 32 | Balance quality vs file size |
| Network Alpha | 16 | Half of rank |
| Optimizer | AdamW8bit | Memory efficient |
| Resolution | 1024,1024 | SDXL native resolution |
| Batch Size | 1 | Required for single GPU |
| Save Every N Steps | 500 | Checkpoint at 500, 1000, 1500, 2000 |

### Step 4 — Evaluate Checkpoints

Test each saved checkpoint at 500-step intervals with:
```
"photo of InfluencerName, smiling, outdoor cafe, golden hour lighting, hyperrealistic"
```
Select the checkpoint with best face fidelity. Move final `.safetensors` to `ComfyUI/models/loras/`.

---

## 8. ComfyUI API — Workflow JSON Structure

The exported API-format workflow is a flat dictionary where each key is a node ID:

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "_meta": {"title": "Load Checkpoint"},
    "inputs": { "ckpt_name": "realvisxlV40.safetensors" }
  },
  "2": {
    "class_type": "LoraLoader",
    "_meta": {"title": "Load LoRA"},
    "inputs": {
      "model": ["1", 0],
      "clip": ["1", 1],
      "lora_name": "influencer_character_v1.safetensors",
      "strength_model": 0.9,
      "strength_clip": 0.9
    }
  },
  "5": {
    "class_type": "IPAdapterFaceID",
    "_meta": {"title": "IPAdapter FaceID"},
    "inputs": {
      "model": ["2", 0],
      "ipadapter": "ip-adapter_sdxl_vit-h.safetensors",
      "image": ["face_loader", 0],
      "weight": 0.85,
      "weight_type": "linear"
    }
  }
}
```

---

## 9. Testing & Validation

### Consistency Test Protocol

Generate 10 images with different random seeds and different prompts:

```python
test_prompts = [
    "photo of InfluencerName, coffee shop, casual outfit, daylight",
    "photo of InfluencerName, tech conference, professional attire",
    "photo of InfluencerName, gym, athletic wear, natural lighting",
    "photo of InfluencerName, outdoor park, summer dress, golden hour",
    "photo of InfluencerName, home office, dark background, monitor glow"
]
```

**Pass criteria:** Face recognition similarity score > 0.85 across all 10 images.

```bash
pip install deepface
```

```python
from deepface import DeepFace
result = DeepFace.verify("reference_face.jpg", "generated_001.jpg", model_name="ArcFace")
print(f"Verified: {result['verified']}, Distance: {result['distance']}")
# Distance < 0.4 = strong match
```

---

## 10. Quality Control Standards

| Metric | Target | Tool |
|--------|--------|------|
| Face similarity to reference | > 0.85 (ArcFace) | DeepFace |
| Image resolution | 1024x1024 minimum | PIL/Pillow |
| NSFW content | 0% | NudeNet or safety checker |
| Generation time | < 45s (RTX 4090), < 3min (RTX 3060) | Internal timer |
| File size (JPEG q=90) | < 2 MB | os.path.getsize |

### Automated QC Script

```python
# qc/image_validator.py
from PIL import Image
from deepface import DeepFace
import os

REFERENCE_FACE = "input/face_reference.jpg"
MIN_SIMILARITY = 0.85

def validate_image(image_path: str) -> dict:
    results = {"path": image_path, "passed": True, "issues": []}

    # Resolution check
    with Image.open(image_path) as img:
        if img.size[0] < 1024 or img.size[1] < 1024:
            results["issues"].append(f"Low resolution: {img.size}")
            results["passed"] = False

    # File size check
    size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if size_mb > 2.0:
        results["issues"].append(f"File too large: {size_mb:.1f} MB")

    # Face similarity check
    try:
        verify = DeepFace.verify(REFERENCE_FACE, image_path,
                                  model_name="ArcFace", enforce_detection=False)
        similarity = 1 - verify["distance"]
        results["face_similarity"] = round(similarity, 3)
        if similarity < MIN_SIMILARITY:
            results["issues"].append(f"Low face similarity: {similarity:.3f}")
            results["passed"] = False
    except Exception as e:
        results["issues"].append(f"Face detection failed: {e}")
        results["passed"] = False

    return results
```

---

*End of Report 02 — AI Influencer Image Generation Pipeline*
