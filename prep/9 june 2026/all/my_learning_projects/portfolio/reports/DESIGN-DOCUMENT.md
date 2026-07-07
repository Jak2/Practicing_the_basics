# DESIGN DOCUMENT
# Autonomous AI Influencer & Social Media Automation System
### Full-Stack Architecture · Technical Specification · Portfolio Prompt Guide

---

**Document Version:** 1.0.0
**Classification:** Master Design Document
**Author:** Senior Systems Architect
**Date:** 2026-03-24
**Status:** Approved for Development

---

## Table of Contents

1. [Project Vision & Goals](#1-project-vision--goals)
2. [System Overview](#2-system-overview)
3. [Full Architecture Diagram](#3-full-architecture-diagram)
4. [Module Breakdown](#4-module-breakdown)
5. [Data Flow Specification](#5-data-flow-specification)
6. [Technology Stack Summary](#6-technology-stack-summary)
7. [Infrastructure Design](#7-infrastructure-design)
8. [Security Architecture](#8-security-architecture)
9. [Scalability & Performance Design](#9-scalability--performance-design)
10. [Development Phases & Milestones](#10-development-phases--milestones)
11. [Risk Register](#11-risk-register)
12. [Portfolio Website Design Prompt](#12-portfolio-website-design-prompt)

---

## 1. Project Vision & Goals

### 1.1 Vision Statement

Build a **fully autonomous, end-to-end AI content production and distribution system** capable of operating 24/7 without human intervention — generating trending short-form video content through a synthetic AI influencer persona and distributing it across all major social media platforms.

### 1.2 Problem Statement

Content creators face three compounding bottlenecks:
- **Time:** Researching, scripting, filming, editing, and posting daily content is a 6-8 hour process per piece.
- **Cost:** Professional video production, voice talent, and social media management costs $2,000–$10,000/month.
- **Consistency:** Human creators face burnout, scheduling conflicts, and creative blocks.

### 1.3 Solution

An AI pipeline that autonomously handles every layer of the content lifecycle — from trend detection to published video — using open-source tooling at near-zero marginal cost per video.

### 1.4 Success Metrics

| Metric | Target (3 months) | Target (12 months) |
|--------|------------------|-------------------|
| Videos produced/day | 3 | 10 |
| Platforms covered | 3 | 5 |
| Avg production time/video | < 8 minutes | < 3 minutes |
| Human intervention required | < 5 min/day | 0 min/day |
| Cost per video | < $0.10 | < $0.02 |
| Combined follower growth (all platforms) | 5,000 | 50,000 |

---

## 2. System Overview

The system is composed of **4 loosely coupled microservices**, each responsible for one stage of the content pipeline. Each service exposes a REST API and communicates asynchronously via HTTP webhooks and a shared PostgreSQL job queue.

```
[STAGE 1]              [STAGE 2]              [STAGE 3]              [STAGE 4]
Orchestration    -->   Image Gen        -->   Video Production  -->   Social Publish
"The Brain"            "The Face"             "The Studio"            "The Megaphone"

LangGraph +            ComfyUI +              LivePortrait +          Twitter API +
CrewAI +               StableDiffusion +      Edge-TTS +              YouTube API +
n8n +                  IP-Adapter +           Whisper +               Meta Graph API +
Ollama                 ControlNet +           FFmpeg                  Playwright (TikTok)
                       LoRA Training
```

### 2.1 Design Principles

| Principle | Application |
|-----------|------------|
| **Autonomy** | No human required in the happy path — full pipeline triggers, runs, and publishes without intervention |
| **Modularity** | Each of the 4 stages is an independent service; any stage can be replaced or upgraded without touching others |
| **Observability** | Every node, job, and API call is logged in structured JSON; dashboards in n8n and Prometheus |
| **Resilience** | All jobs have retry queues, dead-letter states, and error webhooks to n8n for alerting |
| **Cost Efficiency** | All inference runs locally (Ollama + ComfyUI); cloud APIs used only as fallback |
| **Persona Consistency** | Identity locked at both model level (LoRA weights) and prompt level (IP-Adapter + trigger word) |

---

## 3. Full Architecture Diagram

```
+========================================================================+
|                    AUTONOMOUS AI INFLUENCER SYSTEM                     |
+========================================================================+

 EXTERNAL INPUTS                  STAGE 1: ORCHESTRATION ENGINE
 +------------------+             +-------------------------------------+
 | Google Trends    |-----------> |  LangGraph State Machine            |
 | NewsAPI          |             |                                     |
 | Reddit API       |             |  fetch_trends                       |
 +------------------+             |       |                             |
                                  |  rank_select                        |
                                  |       |                             |
                                  |  run_crew (CrewAI)                  |
                                  |    [Researcher]->[Writer]->[Editor]  |
                                  |       |                             |
                                  |  persona_review                     |
                                  |    |          |                     |
                                  |  PASS       FAIL (max 3 retries)   |
                                  |    |          |                     |
                                  |    v          v                     |
                                  |  finalize  revise_node              |
                                  |    |                                |
                                  |  OUTPUT: {script, image_prompt,     |
                                  |           hashtags, metadata}       |
                                  +------------------+------------------+
                                                     |
                                     +---------------v-----------------+
                                     |   STAGE 2: IMAGE GENERATION     |
                                     |                                 |
                                     |  ComfyUI Workflow               |
                                     |                                 |
                                     |  [SDXL Checkpoint]              |
                                     |       + [LoRA: character v1]    |
                                     |       + [IP-Adapter: face ref]  |
                                     |       + [ControlNet: pose]      |
                                     |            |                    |
                                     |  [KSampler Base Pass]           |
                                     |       |                         |
                                     |  [KSampler Refiner Pass]        |
                                     |       |                         |
                                     |  [VAE Decode]                   |
                                     |       |                         |
                                     |  OUTPUT: 1024x1024 JPEG         |
                                     |  + QC (ArcFace similarity check)|
                                     +---------------+-----------------+
                                                     |
                                     +---------------v-----------------+
                                     |   STAGE 3: VIDEO PRODUCTION     |
                                     |                                 |
                                     |  TTS (Edge-TTS / Bark)          |
                                     |    script -> voice.wav          |
                                     |       |                         |
                                     |  LivePortrait                   |
                                     |    image + audio -> MP4 clip    |
                                     |       |                         |
                                     |  Whisper Large-v3               |
                                     |    voice.wav -> word timestamps |
                                     |       |                         |
                                     |  Subtitle Renderer              |
                                     |    timestamps -> subtitles.ass  |
                                     |       |                         |
                                     |  FFmpeg Assembly                |
                                     |    clip + audio + subs +        |
                                     |    bg_music + logo              |
                                     |    -> 1080x1920 final.mp4       |
                                     +---------------+-----------------+
                                                     |
                                     +---------------v-----------------+
                                     |   STAGE 4: SOCIAL PUBLISHING    |
                                     |                                 |
                                     |  Job Queue (PostgreSQL)         |
                                     |  Scheduler (APScheduler)        |
                                     |       |                         |
                                     |  Publisher Router               |
                                     |    |        |        |          |
                                     |  [X]  [YouTube] [Instagram]     |
                                     |    |   (API)    (Meta Graph)    |
                                     |  [TikTok via Playwright]        |
                                     |       |                         |
                                     |  Analytics Fetcher (24h/7d)     |
                                     |  Rate Limiter (Redis)           |
                                     +---------------+-----------------+
                                                     |
                                     +---------------v-----------------+
                                     |   MONITORING & CONTROL          |
                                     |                                 |
                                     |  n8n Dashboard (visual flows,   |
                                     |  alerts, scheduling UI)         |
                                     |  Prometheus + Grafana           |
                                     |  Structured logs (structlog)    |
                                     +----------------------------------+
```

---

## 4. Module Breakdown

### 4.1 Module 1 — Orchestration Engine (The Brain)

| Attribute | Value |
|-----------|-------|
| Primary Report | report-01-ai-orchestration-brain.md |
| Framework | LangGraph 0.2+ |
| Language | Python 3.11 |
| API Port | 8000 |
| Primary Responsibility | Trend detection, content planning, script generation, persona enforcement |

**Key Design Decisions:**
- **LangGraph over plain LangChain:** LangGraph's state machine model enables the persona review loop — the script cycles through `write → review → revise` up to 3 times before being force-finalized. LangChain chains cannot express this cyclic flow.
- **CrewAI for role separation:** Splitting the work into Researcher / Writer / Editor agents prevents the LLM from conflating tasks (a common issue with single-prompt approaches). Each agent has a focused system prompt with minimal scope.
- **Ollama for cost elimination:** All LLM calls run locally. Cloud API (Groq) is configured as a fallback only when the local GPU is under load.
- **Persona pinning via system prompt:** The Reviewer agent's backstory explicitly encodes the influencer's brand voice. The review loop cannot pass until tone, register, and CTA requirements are satisfied.

**State Machine Contract:**
```
AgentState {
  niche:            str           # e.g., "AI technology"
  trending_topics:  List[dict]    # Raw fetch from trend APIs
  selected_topic:   dict          # Ranked winner
  research_notes:   str           # CrewAI Researcher output
  raw_script:       str           # CrewAI Writer output (mutable via revise loop)
  image_prompt:     str           # CrewAI Art Director output
  hashtags:         List[str]     # Finalize node output
  review_passed:    bool          # Reviewer verdict
  review_feedback:  str           # Specific issues (used by revise node)
  retry_count:      int           # Max 3 before force-finalize
  final_payload:    dict          # Consumed by Stage 2 and Stage 4
}
```

---

### 4.2 Module 2 — Image Generation Pipeline (The Face)

| Attribute | Value |
|-----------|-------|
| Primary Report | report-02-ai-influencer-image-pipeline.md |
| Framework | ComfyUI (API mode) |
| Language | Python 3.11 + ComfyUI internals |
| API Port | 8188 (ComfyUI native) |
| Primary Responsibility | Generating character-consistent portrait images for any prompt |

**Key Design Decisions:**
- **Three-layer consistency stack:** No single technique alone achieves reliable identity. The combination of `LoRA (weights) + IP-Adapter (visual prompt) + trigger word (text prompt)` creates overlapping consistency signals that reinforce each other.
- **LoRA trained on the same base model as inference:** Training and inference use `RealVisXL V4.0`. Using different checkpoints breaks the LoRA's learned weights.
- **Two-pass KSampler (Base + Refiner):** The SDXL architecture was designed for two-pass inference. Skipping the refiner pass produces noticeably softer facial details — especially eyes, hair, and skin texture.
- **ArcFace QC gate:** Every generated image is scored against the reference face before being forwarded to Stage 3. Images below 0.85 similarity are regenerated (up to 3 attempts with different seeds).

**Consistency Stack Priority Order:**

```
IP-Adapter weight       → Strongest real-time identity signal
Character LoRA weight   → Baked identity in model weights
Trigger word in prompt  → Semantic anchoring
ControlNet pose         → Structural constraint (optional)
```

---

### 4.3 Module 3 — Video Production Pipeline (The Studio)

| Attribute | Value |
|-----------|-------|
| Primary Report | report-03-ai-video-production-pipeline.md |
| Framework | LivePortrait + FFmpeg + Whisper |
| Language | Python 3.11 |
| API Port | 8002 |
| Primary Responsibility | Animating the influencer image, adding voice, subtitles, and producing the final MP4 |

**Key Design Decisions:**
- **LivePortrait over Wav2Lip/SadTalker:** LivePortrait animates the entire head (eyes, neck, micro-expressions) not just the mouth region. The result is perceptibly more natural and less "deepfake-looking."
- **Edge-TTS as primary TTS engine:** 300+ voices, zero cost, near-instant synthesis. Bark is reserved for premium/hero posts where extra expressiveness justifies the 10x generation time.
- **Whisper for subtitle alignment, not transcription:** We already have the script. Whisper is used purely for its word-level timestamps (forced alignment), which drive the animated TikTok-style subtitle display.
- **ASS subtitle format over SRT:** ASS supports per-word color changes and font styling. This enables the "active word highlighted yellow" effect that increases accessibility and retention.
- **FFmpeg filter_complex for single-pass assembly:** All composition operations (scale, pad, subtitles, audio mix, logo overlay) run in a single FFmpeg invocation. Chaining multiple FFmpeg calls degrades quality with each transcode.

**Audio Mixing Design:**

```
Voice track:       100% volume  (foreground — must be clear)
Background music:  12% volume   (ducked — mood, not distraction)
Music handling:    aloop=-1     (loops seamlessly for any duration)
Mix mode:          amix duration=first  (trims to voice length)
```

---

### 4.4 Module 4 — Social Media Publisher (The Megaphone)

| Attribute | Value |
|-----------|-------|
| Primary Report | report-04-social-media-automation.md |
| Framework | FastAPI + APScheduler + Playwright |
| Language | Python 3.11 |
| API Port | 8001 |
| Primary Responsibility | Scheduled distribution of completed videos to all target platforms |

**Key Design Decisions:**
- **Two-tier architecture (API + Browser Automation):** Official APIs are preferred for reliability and ToS compliance. Browser automation (Playwright) is used only where APIs are unavailable or too restrictive (TikTok).
- **PostgreSQL job queue over Redis Queue:** The job state machine has too many states (scheduled → processing → published/retrying/failed) for a simple queue. PostgreSQL gives queryable history, analytics joins, and ACID guarantees.
- **APScheduler over cron:** APScheduler runs inside the Python process, reads job times from the database, and fires with per-job precision. External cron would require a separate DB query process.
- **Analytics feedback loop:** Fetching engagement metrics at 24h and 7d creates a data asset for future topic selection scoring. High-performing topics are upweighted in Stage 1's `rank_and_select_node`.
- **Playwright session persistence:** TikTok login state is saved to `storage_state.json` and reloaded each run, avoiding the need to re-authenticate and triggering fewer security checks.

---

## 5. Data Flow Specification

### 5.1 Primary Payload — Stage 1 → Stage 2 → Stage 3 → Stage 4

```json
{
  "job_id": "uuid-v4",
  "stage1_output": {
    "topic": "OpenAI releases GPT-5 mini",
    "script": "[HOOK] What if I told you...\n[BODY]...\n[CTA] Follow for more",
    "image_prompt": "photo of InfluencerName, neon tech lab, confident pose, high-detail",
    "hashtags": ["#AI", "#GPT5", "#Tech", "#Innovation"],
    "metadata": {
      "niche": "AI technology",
      "generated_at": "2026-03-24T08:00:00Z",
      "review_retries": 1
    }
  },
  "stage2_output": {
    "image_path": "/outputs/images/job_uuid_v4.jpg",
    "face_similarity_score": 0.91,
    "generation_seed": 1847392847
  },
  "stage3_output": {
    "video_path": "/outputs/videos/job_uuid_v4.mp4",
    "duration_seconds": 42,
    "subtitle_words": 87,
    "tts_engine": "edge-tts",
    "tts_voice": "en-US-JennyNeural"
  },
  "stage4_input": {
    "platforms": ["x", "youtube", "instagram", "tiktok"],
    "caption": "What if I told you AI just changed everything?",
    "hashtags": ["#AI", "#GPT5", "#Tech"],
    "scheduled_time": "2026-03-24T12:00:00Z"
  }
}
```

### 5.2 Service-to-Service Communication

| From | To | Method | Trigger |
|------|----|--------|---------|
| n8n Scheduler | Stage 1 API | HTTP POST `/orchestrate` | CRON: 0 6 * * * |
| Stage 1 API | Stage 2 API | HTTP POST `/generate` | On `finalize_node` completion |
| Stage 2 API | Stage 3 API | HTTP POST `/produce` | On image QC pass |
| Stage 3 API | Stage 4 API | HTTP POST `/publish` | On video assembly complete |
| Stage 4 API | n8n Webhook | HTTP POST `/webhook/alerts` | On job failure |
| Stage 4 Analytics | Stage 1 Ranker | HTTP POST `/feedback` | 24h after publish |

---

## 6. Technology Stack Summary

### 6.1 AI / ML Layer

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| LLM Inference | Ollama | Latest | Local LLM server |
| Primary LLM | Llama 3 8B Instruct | Latest | Script writing, review |
| Agent Framework | LangGraph | 0.2+ | Stateful graph execution |
| Multi-Agent | CrewAI | 0.55+ | Role-based agent delegation |
| Image Generation | Stable Diffusion XL | 1.0 | Base image model |
| Image Checkpoint | RealVisXL V4.0 | 4.0 | Photorealism fine-tune |
| Face Consistency | IP-Adapter ViT-H | SDXL | Face identity conditioning |
| Pose Control | ControlNet OpenPose | SDXL | Body pose enforcement |
| Character LoRA | Custom trained | — | Persona identity weights |
| Workflow UI | ComfyUI | Latest | Image pipeline orchestration |
| Video Animation | LivePortrait | Latest | Facial animation from audio |
| Text-to-Speech | Edge-TTS | 6.1+ | Fast, free neural TTS |
| TTS (Premium) | Bark | 1.0 | Expressive neural TTS |
| Speech Alignment | Faster-Whisper | 1.0+ | Word-level timestamps |
| LoRA Training | Kohya_ss | Latest | Character fine-tuning |

### 6.2 Backend / Infrastructure Layer

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Orchestration API | FastAPI | 0.111+ | REST API gateway for each stage |
| Task Queue | APScheduler | 3.10+ | In-process job scheduling |
| Database | PostgreSQL | 15 | Job state, analytics, history |
| Cache / Rate Limit | Redis | 7 | Rate limit tracking, dedup |
| Automation | n8n | Latest | Visual workflow orchestration |
| Containerization | Docker + Compose | 26 | Service isolation |
| Video Processing | FFmpeg | 6+ | Final video assembly |

### 6.3 Social Platform Layer

| Platform | Integration Method | Auth Type |
|----------|--------------------|-----------|
| X (Twitter) | Tweepy + Twitter API v2 | OAuth 2.0 User Context |
| YouTube | Google API Python Client | OAuth 2.0 + Service Account |
| Instagram Reels | Meta Graph API v20 | Long-lived Access Token |
| Facebook | Meta Graph API v20 | Long-lived Access Token |
| TikTok | Playwright headless browser | Cookie session state |

---

## 7. Infrastructure Design

### 7.1 Docker Compose — Full Stack

```yaml
version: "3.9"

services:
  # ─── Shared Infrastructure ───────────────────────────
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ai_influencer_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=ai_influencer_db
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
    depends_on:
      - postgres

  # ─── Stage 1: Orchestration ──────────────────────────
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  orchestration:
    build: ./orchestration-engine
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis
      - ollama

  # ─── Stage 2: Image Generation ───────────────────────
  comfyui:
    build: ./comfyui-service
    ports:
      - "8188:8188"
    volumes:
      - comfyui_models:/app/models
      - ./outputs/images:/app/output
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  image-api:
    build: ./image-api
    ports:
      - "8003:8003"
    depends_on:
      - comfyui

  # ─── Stage 3: Video Production ───────────────────────
  video-pipeline:
    build: ./video-pipeline
    ports:
      - "8002:8002"
    volumes:
      - ./outputs/images:/app/input/images:ro
      - ./outputs/videos:/app/output
    depends_on:
      - postgres

  # ─── Stage 4: Social Publishing ──────────────────────
  publisher:
    build: ./publisher-service
    ports:
      - "8001:8001"
    volumes:
      - ./outputs/videos:/app/videos:ro
      - ./credentials:/app/credentials:ro
      - ./playwright_state:/app/playwright_state
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  ollama_models:
  comfyui_models:
```

### 7.2 Port Map

| Service | Port | Purpose |
|---------|------|---------|
| n8n Dashboard | 5678 | Visual workflow control panel |
| Orchestration API | 8000 | Stage 1 REST API |
| Publisher API | 8001 | Stage 4 REST API |
| Video Pipeline API | 8002 | Stage 3 REST API |
| Image API | 8003 | Stage 2 REST API wrapper |
| ComfyUI | 8188 | Image generation server (internal) |
| Ollama | 11434 | LLM inference server (internal) |

### 7.3 Networking

All services communicate over a single Docker bridge network (`ai-influencer-net`). Only n8n (5678) needs to be exposed to the host for the dashboard. All other ports are internal-only in production — accessed via nginx reverse proxy with TLS.

---

## 8. Security Architecture

### 8.1 Threat Model

| Threat | Attack Vector | Mitigation |
|--------|--------------|------------|
| Prompt injection | Malicious trend data injected into LLM prompts | Sanitize all external strings; pin system prompt; validate output schema |
| Credential leakage | API keys in environment | Docker secrets; `.env` in `.gitignore`; no keys in logs |
| Session hijacking | TikTok playwright state file | Encrypt `storage_state.json` at rest; rotate session monthly |
| Unauthorized API access | Exposed internal services | nginx + basic auth on all ports; firewall all except 443/80 |
| LLM output abuse | Model generates NSFW/harmful script | Post-generation regex validator; content safety classifier |
| Rate limit bypass | Posting beyond platform limits | Redis rate limiter hard-coded per platform |
| Supply chain attack | Malicious Python packages | Pin all dependencies with exact versions; hash verification |

### 8.2 Secret Management

```
.env file              → Docker secrets injection (never committed)
credentials/ dir       → Volume mount, not baked into image
Playwright state       → Stored outside /app, owner: root, chmod 600
API keys in logs       → structlog: never log values containing "token", "key", "secret"
```

---

## 9. Scalability & Performance Design

### 9.1 Current State (Phase 1)

```
Single server, single GPU
Throughput: ~3 videos/day
Bottleneck: LivePortrait animation (4-8 min/video on RTX 3060)
```

### 9.2 Phase 2 — Horizontal GPU Scaling

```
Add dedicated ComfyUI server (image generation)
Add dedicated Video Pipeline server (LivePortrait)
Shared PostgreSQL job queue coordinates work
Throughput: 10-15 videos/day
```

### 9.3 Phase 3 — Cloud Burst

```
GPU burst via RunPod.io for peak demand
Orchestration and publishing remain on-prem
Throughput: 50+ videos/day
```

### 9.4 Performance Benchmarks

| Stage | RTX 3060 (12GB) | RTX 4090 (24GB) |
|-------|----------------|----------------|
| Stage 1: Script generation | 45s | 15s |
| Stage 2: Image generation | 3 min | 30s |
| Stage 3: TTS (60s script) | 3s | 3s |
| Stage 3: LivePortrait animation | 5 min | 50s |
| Stage 3: Whisper transcription | 20s | 8s |
| Stage 3: FFmpeg assembly | 15s | 12s |
| Stage 4: Upload (all platforms) | 3 min | 3 min |
| **Total per video** | **~12 min** | **~5 min** |

---

## 10. Development Phases & Milestones

### Phase 1 — Core Pipeline (Weeks 1-4)
- [ ] Stage 1: LangGraph graph compiles and produces valid `AgentState`
- [ ] Stage 1: CrewAI crew produces research + script + image prompt
- [ ] Stage 1: Persona review loop passes consistently
- [ ] Stage 2: ComfyUI runs in API mode and returns an image
- [ ] Stage 2: Character LoRA trained, face similarity > 0.85
- [ ] Stage 3: Edge-TTS produces voice.wav from script
- [ ] Stage 3: LivePortrait animates image with audio
- [ ] Stage 3: FFmpeg assembles final 1080x1920 MP4

### Phase 2 — Publishing & Automation (Weeks 5-6)
- [ ] Stage 4: X API publishes test video
- [ ] Stage 4: YouTube Shorts API publishes test video
- [ ] Stage 4: Instagram Reels via Meta Graph API publishes
- [ ] Stage 4: TikTok Playwright session established, test upload passes
- [ ] n8n: Full pipeline CRON trigger end-to-end without manual intervention
- [ ] n8n: Failure alert webhook fires on simulated error

### Phase 3 — Observability & Optimization (Weeks 7-8)
- [ ] Prometheus metrics exported from all 4 services
- [ ] Grafana dashboard shows pipeline health, video throughput, error rates
- [ ] Analytics feedback loop: 24h post metrics fetched and stored
- [ ] Topic ranker ingests analytics for scoring improvement
- [ ] QC gate: Regeneration on failed face similarity working end-to-end

---

## 11. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Platform API changes (Meta, X) | High | High | Abstract publisher behind interface; monitor API changelogs |
| TikTok UI changes break Playwright | Medium | Medium | Screenshot-on-failure debugging; UI selector version pinning |
| LoRA overfitting (face looks cartoonish) | Medium | Medium | Save checkpoints every 500 steps; evaluate each before use |
| Ollama OOM on 8GB VRAM | High | Low | Use `--lowvram` flag; offload layers to CPU RAM |
| LivePortrait produces uncanny results | Low | High | Add human-review gate for first 30 videos; build rejection classifier |
| TOS violation (platform automated posting) | Medium | High | Use official APIs where available; rate-limit conservatively; never use aggressive scraping |
| OpenAI claims on Ollama model outputs | Low | Low | Use fully open-weight models (Llama 3, Mistral) |

---

## 12. Portfolio Website Design Prompt

The following is a **comprehensive design prompt** for creating a portfolio website that showcases this AI Influencer Automation System project. This prompt is written for use with any design AI (v0, Lovable, Bolt, Claude, or a human designer).

---

### 12.1 The Design Prompt

```
You are a world-class UI/UX designer and frontend developer. Design and build
a portfolio website that showcases the "Autonomous AI Influencer System" — a
full-stack AI automation project that generates, animates, and publishes AI
influencer content to social media without any human intervention.

═══════════════════════════════════════════════════════════════════════
DESIGN LANGUAGE
═══════════════════════════════════════════════════════════════════════

Visual Style:     Neo-brutalism meets high-tech dark UI
Color Palette:
  Primary:        #0A0A0A  (near-black background)
  Surface:        #111111  (card backgrounds)
  Border:         #222222  (default borders)
  Accent:         #C8FF00  (electric lime — primary CTA and highlights)
  Accent 2:       #00D4FF  (cyan — secondary highlight, data flows)
  Text Primary:   #F5F5F5  (near-white)
  Text Secondary: #888888  (muted gray)

Typography:
  Headlines:      Space Grotesk or Clash Display (bold, modern, geometric)
  Body:           Inter or DM Sans
  Code/Mono:      JetBrains Mono (for technical details, stats, code snippets)

Aesthetic References:
  - Linear.app dark mode (clean, precise, spacious)
  - Vercel homepage (confident tech-forward product marketing)
  - Raycast website (beautiful developer tool showcase)

DO NOT use:
  - Light backgrounds as primary theme
  - Pastel colors
  - Rounded-corner-only cards (some sharp borders are intentional)
  - Generic gradient hero backgrounds
  - Clip art or generic stock illustrations

═══════════════════════════════════════════════════════════════════════
PAGE STRUCTURE (Single Page, Scroll-Based)
═══════════════════════════════════════════════════════════════════════

── SECTION 1: HERO ──────────────────────────────────────────────────

Layout: Full viewport height. Dark background. Left-aligned content.

Headline (large, bold):
  "The AI That Creates,
   Animates & Posts
   Content While You Sleep."

Sub-headline (muted, medium):
  "A fully autonomous pipeline — from trending topics to published
   short-form video — powered by LangGraph, Stable Diffusion,
   and LivePortrait. Zero human intervention."

CTA Buttons (side by side):
  [View Architecture]  ← primary, accent color (#C8FF00, black text)
  [See Source Code]    ← secondary, outline style

Right side / background element:
  Animated pipeline flow diagram. Three glowing nodes connected
  by pulsing lines. Labels: "Brain" → "Face" → "Studio" → "Megaphone"
  Nodes pulse with a subtle animated glow. Lines animate left-to-right.
  Colors: nodes in #C8FF00, lines in #00D4FF on #0A0A0A.

Stats row at bottom of hero (inline, separated by dividers):
  ┌─────────────┬──────────────┬──────────────┬───────────────┐
  │ 4 Platforms │ <$0.10/video │  ~5 min/post │ 0 min/day     │
  │  Automated  │ Production   │  End-to-End  │ Human Input   │
  └─────────────┴──────────────┴──────────────┴───────────────┘
  Use JetBrains Mono for numbers. Small muted label below each.

── SECTION 2: HOW IT WORKS ──────────────────────────────────────────

Headline: "Four Stages. One Pipeline. Infinite Content."

Layout: Horizontal scrollable cards on desktop, vertical stack on mobile.
Each card represents one stage. Cards have thick left border in accent color.
Hover state: card lifts (box-shadow) and border intensifies.

Card 1 — THE BRAIN
  Icon:        Neural network / graph icon
  Badge:       "Stage 01" in mono font
  Title:       "Orchestration Engine"
  Tech tags:   [LangGraph] [CrewAI] [Ollama] [n8n]
  Description: "Fetches trending topics, assigns specialized AI agents
                (Researcher, Writer, Editor), and runs a persona review
                loop until the script matches the brand voice."
  Key metric:  "3-layer review loop · Max 3 retries · Local LLM inference"

Card 2 — THE FACE
  Icon:        Portrait / aperture icon
  Badge:       "Stage 02"
  Title:       "Image Generation"
  Tech tags:   [Stable Diffusion XL] [IP-Adapter] [ControlNet] [LoRA]
  Description: "Generates photorealistic, character-consistent portrait
                images using a triple-layer identity stack: trained LoRA
                weights, IP-Adapter face conditioning, and trigger words."
  Key metric:  "ArcFace similarity > 0.85 · QC gate · 1024×1024 output"

Card 3 — THE STUDIO
  Icon:        Video camera / waveform icon
  Badge:       "Stage 03"
  Title:       "Video Production"
  Tech tags:   [LivePortrait] [Edge-TTS] [Whisper] [FFmpeg]
  Description: "Converts still image + script to a fully animated talking-
                head video. Adds voice, word-highlighted captions, ducked
                background music, and branding."
  Key metric:  "1080×1920 · 9:16 vertical · H.264 AAC · 30fps"

Card 4 — THE MEGAPHONE
  Icon:        Broadcast / satellite icon
  Badge:       "Stage 04"
  Title:       "Social Publishing"
  Tech tags:   [Twitter API] [YouTube API] [Meta Graph API] [Playwright]
  Description: "Schedules and distributes final videos across all major
                platforms. Uses official APIs where available; Playwright
                headless automation for TikTok."
  Key metric:  "5 platforms · Retry queue · Analytics feedback loop"

── SECTION 3: ARCHITECTURE DIAGRAM ─────────────────────────────────

Headline: "Architecture at a Glance"
Sub:      "Four loosely coupled microservices. One PostgreSQL job queue.
           Complete observability."

Full-width interactive diagram:
  Show the 4 services as connected boxes with arrows.
  Use a dark grid background (#0A0A0A with subtle dot grid).
  Each service box:
    - Dark surface (#111111)
    - Accent border on hover
    - Clicking shows a tooltip/popup with: Port, Framework, Key responsibility
  Connection arrows animate on page load (draw-on effect).

  Add a legend row below:
  ● Cyan arrows  = data flow (payload passing between services)
  ● Lime nodes   = compute-heavy services (GPU required)
  ● Gray nodes   = lightweight services (CPU only)

── SECTION 4: TECH STACK ────────────────────────────────────────────

Headline: "Built With"

Layout: Masonry or CSS grid of tech badges.
Each badge is a pill/chip with the technology name and a small icon.
Group them in 4 rows labeled: AI/ML · Backend · Infrastructure · Platforms

Style: Dark surface chips. Hover state adds accent glow. Mono font for names.

═══════════════════════════════════════════════════════════════════════
FEATURED BADGES (include all of these):
AI/ML row:
  LangGraph · CrewAI · LangChain · Ollama · Llama 3 · Stable Diffusion XL
  IP-Adapter · ControlNet · LivePortrait · Edge-TTS · Bark · Whisper
  Kohya_ss · ComfyUI

Backend row:
  Python 3.11 · FastAPI · APScheduler · PostgreSQL · Redis · Playwright

Infrastructure row:
  Docker · Docker Compose · n8n · Prometheus · Grafana · FFmpeg

Platforms row:
  X (Twitter) API · YouTube Data API v3 · Meta Graph API · TikTok

═══════════════════════════════════════════════════════════════════════

── SECTION 5: PERFORMANCE METRICS ──────────────────────────────────

Headline: "Production Benchmarks"

Layout: 2x4 grid of metric cards. Dark surface, accent border on left.
Each card:
  Large number (JetBrains Mono, accent color)
  Small label below (muted gray)
  Optional: small sparkline or progress bar

Metrics to display:
  ~5 min     End-to-end (RTX 4090)
  ~12 min    End-to-end (RTX 3060)
  $0.10      Max cost per video
  4          Social platforms
  0.85+      ArcFace face similarity
  3          Max review retries
  1080×1920  Output resolution
  3           Daily video target

── SECTION 6: CODE SHOWCASE ─────────────────────────────────────────

Headline: "Under the Hood"

Layout: Tab-based code viewer. 4 tabs, one per pipeline stage.
Use a syntax-highlighted code block (dark theme, accent line numbers).
Show a representative ~15-20 line snippet from each stage.
Include copy-to-clipboard button.

Tab 1: "Orchestration" → LangGraph graph_builder.py snippet
Tab 2: "Image Gen"     → generator.py inject_prompt snippet
Tab 3: "Video"         → video_assembler.py assemble() snippet
Tab 4: "Publish"       → x_publisher.py publish() snippet

── SECTION 7: PROJECT LINKS ─────────────────────────────────────────

Headline: "Explore the Project"

3-column card layout:
  Card 1: [GitHub Repository]     → link to repo
  Card 2: [Full Design Document]  → link to DESIGN-DOCUMENT.md
  Card 3: [Technical Reports]     → link to reports/ folder

Each card: dark surface, large icon, title, one-line description, arrow CTA.

── SECTION 8: FOOTER ────────────────────────────────────────────────

Left: Name + tagline ("Senior Systems Engineer · AI Automation")
Center: Navigation links (Home, Projects, About, Contact)
Right: Social icons (GitHub, LinkedIn, X)
Bottom row: "Built with Claude Code" + copyright

═══════════════════════════════════════════════════════════════════════
INTERACTION & ANIMATION GUIDELINES
═══════════════════════════════════════════════════════════════════════

Page load:     Stagger-fade-in for hero elements (50ms intervals)
Scroll reveal: Each section fades in + slides up 20px on first viewport entry
               Use Intersection Observer. Easing: cubic-bezier(0.16,1,0.3,1)

Pipeline nodes: Subtle pulse animation (scale 1.0 → 1.03 → 1.0, 2s loop)
Pipeline lines: Traveling dot along path (CSS animation or SVG stroke-dashoffset)
Card hover:    transform: translateY(-4px) + box-shadow upgrade (200ms ease)
Button hover:  Background shifts from accent to accent+10% brightness
Stats numbers: Count-up animation on first viewport entry (1.5s duration)

Performance requirements:
  Core Web Vitals: LCP < 2.5s, CLS < 0.1, FID < 100ms
  No heavy JS frameworks needed — vanilla JS + CSS animations preferred
  If using a framework: Next.js with static export or Astro preferred
  Images: WebP format, lazy-loaded, explicit width/height

═══════════════════════════════════════════════════════════════════════
RESPONSIVE BREAKPOINTS
═══════════════════════════════════════════════════════════════════════

Mobile  (< 640px):   Single column. Stats wrap 2x2. Code viewer scrollable.
Tablet  (640–1024px): 2-column cards. Side-by-side hero layout collapsed.
Desktop (> 1024px):  Full layout as described. Architecture diagram full-width.

═══════════════════════════════════════════════════════════════════════
ACCESSIBILITY
═══════════════════════════════════════════════════════════════════════

- All color contrasts must pass WCAG AA (min 4.5:1 for body text)
- Animated elements must respect prefers-reduced-motion
- All interactive elements have visible focus indicators
- Code blocks have aria-label for screen readers
- Dark mode is the default (no light mode toggle required for this project)
```

---

### 12.2 Suggested Page Route Structure (if multi-page)

```
/                    → Portfolio home (all projects listed)
/projects/ai-influencer  → This project's dedicated page (the design above)
/reports             → Index of the 4 technical reports
/reports/01-brain    → Report 01
/reports/02-images   → Report 02
/reports/03-video    → Report 03
/reports/04-social   → Report 04
```

### 12.3 Recommended Implementation Stack

| Approach | Stack | Best For |
|----------|-------|---------|
| Simplest | HTML + Tailwind CSS + Alpine.js | Fast build, no framework overhead |
| Recommended | Astro 4 + Tailwind CSS | Static site, markdown reports, great performance |
| Feature-rich | Next.js 14 + Tailwind + Framer Motion | If animations are priority |

---

*End of Master Design Document*
*Cross-reference: report-01, report-02, report-03, report-04*
