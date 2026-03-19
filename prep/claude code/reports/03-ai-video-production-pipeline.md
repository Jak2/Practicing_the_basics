# PROJECT REPORT 03
# AI Character Video Production & Editing Pipeline
### LivePortrait · Edge-TTS · Bark · FFmpeg · MoviePy · Whisper

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
7. [Audio Pipeline](#audio-pipeline)
8. [Video Animation Pipeline](#video-animation-pipeline)
9. [Post-Production & Editing](#post-production--editing)
10. [Output Specifications & Platform Formats](#output-specifications--platform-formats)

---

## 1. Executive Summary

The AI Video Production Pipeline converts three raw inputs — a **generated still image** (from Report 02), a **script** (from Report 01), and a **background music track** — into a fully edited, platform-ready short-form video for Reels, TikTok, and YouTube Shorts.

The pipeline runs through four sequential stages:

1. **Text-to-Speech (TTS):** Converts the script to a high-quality voiceover using Edge-TTS (fast, free) or Bark (realistic, slower). Outputs a timestamped `.wav` file.
2. **Facial Animation:** Uses **LivePortrait** to animate the static influencer image so the face lip-syncs to the audio. Outputs a silent `.mp4` clip.
3. **Subtitle Generation:** Passes the audio through **Whisper** for word-level timestamps, then renders styled on-screen subtitles.
4. **Final Assembly:** **FFmpeg** combines the animated clip, background music (ducked under voice), subtitles, and branding elements into the final platform-optimized video.

---

## 2. System Requirements

### 2.1 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | NVIDIA RTX 3060 8GB | NVIDIA RTX 4090 24GB |
| CPU | 8-core | 16-core |
| RAM | 16 GB | 32 GB |
| Storage | 50 GB SSD | 500 GB NVMe |
| OS | Ubuntu 22.04 | Ubuntu 22.04 LTS |
| CUDA | 12.1+ | 12.4 |

**GPU memory usage breakdown:**

| Stage | VRAM Usage |
|-------|-----------|
| LivePortrait animation | 4-8 GB |
| Whisper Large-v3 | 6 GB |
| Combined (sequential) | 8 GB max |

### 2.2 Python Dependencies

```
torch>=2.3.0
torchaudio>=2.3.0
onnxruntime-gpu>=1.18.0
edge-tts>=6.1.9
openai-whisper>=20231117
faster-whisper>=1.0.0
moviepy==1.0.3
ffmpeg-python>=0.2.0
pillow>=10.3.0
librosa>=0.10.2
scipy>=1.13.0
numpy>=1.26.0
bark>=1.0.0
structlog>=24.2.0
```

---

## 3. Architecture Overview

### 3.1 Full Pipeline Diagram

```
INPUT: { image_path, script_text, background_music_path }
          |
          v
+----------------------------------------------------------+
|                 STAGE 1: TEXT-TO-SPEECH                  |
|                                                          |
|  script_text ---> [Edge-TTS / Bark] ---> voice.wav      |
+----------------------------------------------------------+
          |
          v  voice.wav
+----------------------------------------------------------+
|               STAGE 2: FACIAL ANIMATION                  |
|                                                          |
|  image_path ---+                                         |
|                +--> [LivePortrait] --> talking_head.mp4  |
|  voice.wav  ---+    (audio driven)    (silent clip)     |
+----------------------------------------------------------+
          |
          v  talking_head.mp4
+----------------------------------------------------------+
|              STAGE 3: SUBTITLE GENERATION                |
|                                                          |
|  voice.wav ---> [Whisper Large-v3] ---> words[]         |
|                   word-level timestamps                  |
|                        |                                 |
|                        v                                 |
|              [Subtitle Renderer] ---> subtitles.ass      |
|              (TikTok style: 3 words at a time)           |
+----------------------------------------------------------+
          |
          v  talking_head.mp4 + voice.wav + subs.ass + bg_music
+----------------------------------------------------------+
|              STAGE 4: FINAL ASSEMBLY (FFmpeg)            |
|                                                          |
|  talking_head.mp4 --+                                   |
|  voice.wav ---------+                                   |
|  bg_music.mp3 ------+--> [FFmpeg] --> final_output.mp4  |
|  subs.ass ----------+    audio mix   1080x1920 (9:16)   |
|  logo_overlay.png --+    subtitles   30fps, H.264, AAC  |
+----------------------------------------------------------+
          |
          v
     OUTPUT: final_output.mp4 (platform-ready)
```

### 3.2 Audio Mix Architecture

```
voice.wav    ------------------------------------------  Vol: 100%
bg_music.mp3 ------------------------------------------  Vol: 12% (ducked)
             (loops indefinitely, trimmed to voice length)
                              |
                              v
                      mixed_audio.aac
```

---

## 4. Component Deep Dive

### 4.1 LivePortrait — State-of-the-Art Facial Animation

LivePortrait uses an **implicit keypoint-based motion transfer** approach. It works out-of-the-box on any portrait photo without training.

**How it works:**
1. Extracts appearance feature maps from the source image (your influencer)
2. Extracts motion keypoints from a driving audio signal
3. Warps the source appearance to match the driving motion
4. Outputs a photorealistic animation with natural head movements, eye blinks, micro-expressions

**Key advantage over Wav2Lip/SadTalker:** LivePortrait animates the entire head (neck, eyes, micro-expressions) not just lips — far more natural results.

### 4.2 Edge-TTS — Microsoft Azure TTS (Free)

Edge-TTS reverse-engineers Microsoft Edge's read-aloud feature (Azure Cognitive Services TTS). Provides 300+ voices in 60+ languages at zero cost.

**Best voices for a young AI influencer:**

| Voice | Style |
|-------|-------|
| `en-US-JennyNeural` | Conversational, friendly, clear |
| `en-US-AriaNeural` | Expressive, modern |
| `en-US-GuyNeural` | Male, tech-forward |
| `en-GB-SoniaNeural` | British, professional |

### 4.3 Whisper — Word-Level Transcription for Subtitles

OpenAI Whisper Large-v3 maps words to precise timestamps in the audio. Used here for **forced alignment** to drive animated subtitles, NOT for transcription (we already have the script).

### 4.4 FFmpeg Filter Complex

FFmpeg's `filter_complex` system is used to:
- Scale and letterbox the animated video to 1080x1920
- Burn in ASS-format subtitles with custom fonts and TikTok-style word highlighting
- Mix voice + looped background music with volume ducking
- Overlay the logo watermark at a fixed position

---

## 5. Environment Setup & Configuration

### 5.1 Install System Dependencies

```bash
# Ubuntu 22.04
sudo apt update && sudo apt install -y ffmpeg python3.11 python3.11-venv python3-pip git

# Verify FFmpeg has required codecs
ffmpeg -version | grep "libx264\|libass\|libopus"
```

### 5.2 Install Python Environment

```bash
python3.11 -m venv video_env
source video_env/bin/activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install onnxruntime-gpu
pip install edge-tts openai-whisper faster-whisper
pip install moviepy==1.0.3 ffmpeg-python
pip install librosa scipy numpy pillow bark structlog
```

### 5.3 Install LivePortrait

```bash
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait
pip install -r requirements.txt

# Download pretrained models (auto on first run)
python script/download_models.py
```

### 5.4 Project Directory Structure

```
video-pipeline/
+-- src/
|   +-- main.py
|   +-- tts/
|   |   +-- edge_tts_client.py
|   |   +-- bark_client.py
|   |   +-- tts_factory.py
|   +-- animation/
|   |   +-- liveportrait_client.py
|   +-- subtitles/
|   |   +-- transcriber.py
|   |   +-- subtitle_renderer.py
|   +-- assembly/
|   |   +-- video_assembler.py
|   +-- config/
|       +-- settings.py
+-- assets/
|   +-- music/                   # Background music library (.mp3)
|   +-- fonts/                   # Caption fonts (.ttf)
|   +-- branding/                # Logo, watermark (.png)
+-- tmp/                         # Intermediate files (auto-cleaned)
+-- output/                      # Final MP4 outputs
+-- LivePortrait/                # Cloned repo
```

---

## 6. Step-by-Step Implementation

### Step 1 — TTS Factory

```python
# src/tts/tts_factory.py
from enum import Enum

class TTSEngine(str, Enum):
    EDGE = "edge"
    BARK = "bark"

def get_tts_engine(engine: TTSEngine = TTSEngine.EDGE):
    if engine == TTSEngine.EDGE:
        from src.tts.edge_tts_client import EdgeTTSClient
        return EdgeTTSClient()
    elif engine == TTSEngine.BARK:
        from src.tts.bark_client import BarkTTSClient
        return BarkTTSClient()
    raise ValueError(f"Unknown TTS engine: {engine}")
```

### Step 2 — Edge-TTS Client

```python
# src/tts/edge_tts_client.py
import asyncio
import edge_tts
from pathlib import Path
import structlog

log = structlog.get_logger()

class EdgeTTSClient:
    """
    High-quality, free TTS using Microsoft Edge voices.
    Fast (< 3s for 60s script), zero cost. Recommended for production.
    """

    def __init__(
        self,
        voice: str = "en-US-JennyNeural",
        rate: str = "+10%",     # Slightly faster = more energetic
        pitch: str = "+5Hz",    # Slightly higher = youthful
        volume: str = "+0%"
    ):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

    async def synthesize(self, text: str, output_path: str) -> dict:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        communicate = edge_tts.Communicate(
            text=text, voice=self.voice,
            rate=self.rate, pitch=self.pitch, volume=self.volume
        )

        word_boundaries = []
        audio_chunks = []

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_boundaries.append({
                    "word": chunk["text"],
                    "start_ms": chunk["offset"] / 10000,
                    "duration_ms": chunk["duration"] / 10000
                })

        with open(output_path, "wb") as f:
            for chunk in audio_chunks:
                f.write(chunk)

        if word_boundaries:
            last = word_boundaries[-1]
            duration_ms = last["start_ms"] + last["duration_ms"]
        else:
            duration_ms = 0

        log.info("tts.synthesize.complete",
                 words=len(word_boundaries), duration_s=round(duration_ms / 1000, 1))

        return {
            "audio_path": str(output_path),
            "duration_ms": duration_ms,
            "word_boundaries": word_boundaries
        }

    def synthesize_sync(self, text: str, output_path: str) -> dict:
        return asyncio.run(self.synthesize(text, output_path))
```

### Step 3 — Bark TTS Client (High-Realism Alternative)

```python
# src/tts/bark_client.py
import scipy.io.wavfile as wav
from bark import SAMPLE_RATE, generate_audio, preload_models
from pathlib import Path

class BarkTTSClient:
    """
    Neural TTS using Suno's Bark model.
    Highly expressive — supports [laughs], [sighs], [music] tokens.
    Slower than Edge-TTS. Use for premium/hero content.
    """

    VOICE_PRESETS = {
        "young_female_us": "v2/en_speaker_9",
        "young_male_us": "v2/en_speaker_6",
        "professional_female": "v2/en_speaker_3",
    }

    def __init__(self, voice_preset: str = "young_female_us"):
        self.voice_preset = self.VOICE_PRESETS.get(voice_preset, voice_preset)
        preload_models()

    def synthesize_sync(self, text: str, output_path: str) -> dict:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        audio_array = generate_audio(text, history_prompt=self.voice_preset)
        wav.write(str(output_path), SAMPLE_RATE, audio_array)

        duration_ms = (len(audio_array) / SAMPLE_RATE) * 1000
        return {
            "audio_path": str(output_path),
            "duration_ms": duration_ms,
            "word_boundaries": []  # Bark doesn't provide word timestamps
        }
```

---

## 7. Audio Pipeline

### Step 4 — Whisper Subtitle Alignment

```python
# src/subtitles/transcriber.py
from faster_whisper import WhisperModel

class AudioTranscriber:
    """
    Uses faster-whisper (CTranslate2 backend) for 4x faster inference.
    Produces word-level timestamps for subtitle animation.
    """

    def __init__(self, model_size: str = "large-v3", device: str = "cuda"):
        self.model = WhisperModel(model_size, device=device, compute_type="float16")

    def transcribe_with_timestamps(self, audio_path: str) -> list[dict]:
        """Returns: [{"word": "Hello", "start": 0.24, "end": 0.58}, ...]"""
        segments, _ = self.model.transcribe(
            audio_path,
            word_timestamps=True,
            language="en",
            vad_filter=True
        )

        words = []
        for segment in segments:
            for word in segment.words:
                words.append({
                    "word": word.word.strip(),
                    "start": round(word.start, 3),
                    "end": round(word.end, 3)
                })
        return words
```

### Step 5 — ASS Subtitle Renderer (TikTok Style)

```python
# src/subtitles/subtitle_renderer.py
from pathlib import Path

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},72,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,60,60,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def _ts(seconds: float) -> str:
    """Convert seconds to ASS timestamp H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def render_subtitles(
    words: list[dict],
    output_path: str,
    font: str = "Montserrat",
    words_per_chunk: int = 3,
    highlight_color: str = "&H0000FFFF"  # Yellow highlight
) -> str:
    """
    Generate styled ASS subtitle file.
    TikTok-style: 3 words at a time, active word highlighted yellow.
    """
    lines = [ASS_HEADER.format(font=font)]
    chunks = [words[i:i + words_per_chunk] for i in range(0, len(words), words_per_chunk)]

    for chunk in chunks:
        for active_idx, active_word in enumerate(chunk):
            seg_start = active_word["start"]
            seg_end = active_word["end"]

            parts = []
            for idx, w in enumerate(chunk):
                if idx == active_idx:
                    parts.append(f"{{\\c{highlight_color}}}{w['word']}{{\\c&H00FFFFFF&}}")
                else:
                    parts.append(w["word"])

            text = " ".join(parts)
            lines.append(f"Dialogue: 0,{_ts(seg_start)},{_ts(seg_end)},Default,,0,0,0,,{text}")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8-sig")
    return str(output_path)
```

---

## 8. Video Animation Pipeline

### Step 6 — LivePortrait Client

```python
# src/animation/liveportrait_client.py
import subprocess
from pathlib import Path
import structlog

log = structlog.get_logger()
LIVEPORTRAIT_DIR = Path("LivePortrait")

class LivePortraitClient:
    """
    Drives a static portrait image with audio using LivePortrait.
    Creates a photorealistic talking-head video.
    """

    def animate(
        self,
        source_image_path: str,
        driving_audio_path: str,
        output_path: str,
        output_fps: int = 25
    ) -> str:
        """
        Animate source image using audio as driving signal.
        Returns path to the generated silent MP4.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "python", str(LIVEPORTRAIT_DIR / "inference.py"),
            "--source_image", str(source_image_path),
            "--driving_audio", str(driving_audio_path),
            "--output_dir", str(output_path.parent),
            "--output_name", output_path.stem,
            "--flag_relative_motion", "True",
            "--flag_do_crop", "True",
            "--flag_pasteback", "True",
            "--output_fps", str(output_fps),
        ]

        log.info("liveportrait.animate.start", source=source_image_path)
        result = subprocess.run(cmd, cwd=LIVEPORTRAIT_DIR, capture_output=True,
                                text=True, timeout=600)

        if result.returncode != 0:
            raise RuntimeError(f"LivePortrait failed:\n{result.stderr}")

        animated_path = output_path.parent / f"{output_path.stem}_animated.mp4"
        log.info("liveportrait.animate.complete", output=str(animated_path))
        return str(animated_path)
```

---

## 9. Post-Production & Editing

### Step 7 — Final Assembly with FFmpeg

```python
# src/assembly/video_assembler.py
import subprocess
import random
from pathlib import Path
from typing import Optional
import structlog

log = structlog.get_logger()

class VideoAssembler:
    """
    Assembles all components into the final platform-ready video using FFmpeg.

    Final output spec:
    - Resolution: 1080x1920 (9:16 vertical)
    - FPS: 30
    - Video codec: H.264 (libx264), CRF 18
    - Audio codec: AAC 192kbps
    - Subtitles: Burned in (ASS format)
    """

    MUSIC_DIR = Path("assets/music")
    LOGO_PATH = Path("assets/branding/logo_watermark.png")

    def assemble(
        self,
        animated_video_path: str,
        voice_audio_path: str,
        subtitles_path: str,
        output_path: str,
        background_music_path: Optional[str] = None,
        voice_volume: float = 1.0,
        music_volume: float = 0.12,
        add_logo: bool = True,
        target_resolution: tuple = (1080, 1920)
    ) -> str:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if background_music_path is None:
            background_music_path = self._pick_random_music()

        w, h = target_resolution
        has_logo = add_logo and self.LOGO_PATH.exists()
        has_music = background_music_path is not None

        inputs = ["-i", str(animated_video_path), "-i", str(voice_audio_path)]
        if has_music:
            inputs += ["-i", str(background_music_path)]
        if has_logo:
            inputs += ["-i", str(self.LOGO_PATH)]

        escaped_subs = subtitles_path.replace("\\", "/").replace(":", "\\:")
        filter_parts = [
            f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[scaled_v]",
            f"[scaled_v]subtitles='{escaped_subs}'[subbed_v]",
        ]

        if has_logo:
            filter_parts.append("[subbed_v][3:v]overlay=W-w-30:H-h-30[logo_v]")
            video_out = "[logo_v]"
        else:
            video_out = "[subbed_v]"

        filter_parts.append(f"{video_out}copy[final_v]")

        if has_music:
            filter_parts.append(
                f"[1:a]volume={voice_volume}[voice];"
                f"[2:a]volume={music_volume},aloop=loop=-1:size=2e+09[looped_music];"
                f"[voice][looped_music]amix=inputs=2:duration=first:dropout_transition=3[final_a]"
            )
        else:
            filter_parts.append(f"[1:a]volume={voice_volume}[final_a]")

        filter_complex = ";".join(filter_parts)

        cmd = (
            ["ffmpeg", "-y"] + inputs + [
                "-filter_complex", filter_complex,
                "-map", "[final_v]",
                "-map", "[final_a]",
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "18",
                "-c:a", "aac",
                "-b:a", "192k",
                "-ar", "44100",
                "-shortest",
                "-movflags", "+faststart",
                str(output_path)
            ]
        )

        log.info("ffmpeg.assemble.start", output=str(output_path))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg assembly failed:\n{result.stderr}")

        size_mb = output_path.stat().st_size / (1024 * 1024)
        log.info("ffmpeg.assemble.complete", size_mb=round(size_mb, 2))
        return str(output_path)

    def _pick_random_music(self) -> Optional[str]:
        files = list(self.MUSIC_DIR.glob("*.mp3")) + list(self.MUSIC_DIR.glob("*.wav"))
        return str(random.choice(files)) if files else None
```

### Step 8 — Pipeline Orchestrator (FastAPI)

```python
# src/main.py
import uuid
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.tts.tts_factory import get_tts_engine, TTSEngine
from src.animation.liveportrait_client import LivePortraitClient
from src.subtitles.transcriber import AudioTranscriber
from src.subtitles.subtitle_renderer import render_subtitles
from src.assembly.video_assembler import VideoAssembler

app = FastAPI(title="Video Production Pipeline")

whisper = AudioTranscriber(model_size="large-v3", device="cuda")
assembler = VideoAssembler()
animator = LivePortraitClient()

job_store: dict = {}

class VideoRequest(BaseModel):
    script: str
    image_path: str
    output_name: Optional[str] = None
    tts_engine: TTSEngine = TTSEngine.EDGE
    tts_voice: str = "en-US-JennyNeural"
    background_music: Optional[str] = None

@app.post("/produce")
async def produce_video(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_store[job_id] = {"status": "queued"}
    background_tasks.add_task(_run_pipeline, job_id, request)
    return {"job_id": job_id, "status": "queued"}

async def _run_pipeline(job_id: str, request: VideoRequest):
    tmp_dir = Path(f"tmp/{job_id}")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    try:
        job_store[job_id]["status"] = "tts"
        tts = get_tts_engine(request.tts_engine)
        tts_result = tts.synthesize_sync(request.script, str(tmp_dir / "voice.wav"))

        job_store[job_id]["status"] = "animation"
        animated_path = animator.animate(
            source_image_path=request.image_path,
            driving_audio_path=tts_result["audio_path"],
            output_path=str(tmp_dir / "talking_head.mp4")
        )

        job_store[job_id]["status"] = "subtitles"
        words = whisper.transcribe_with_timestamps(tts_result["audio_path"])
        subs_path = render_subtitles(words, str(tmp_dir / "subtitles.ass"))

        job_store[job_id]["status"] = "assembly"
        output_name = request.output_name or f"video_{job_id[:8]}"
        final_path = assembler.assemble(
            animated_video_path=animated_path,
            voice_audio_path=tts_result["audio_path"],
            subtitles_path=subs_path,
            output_path=f"output/{output_name}.mp4",
            background_music_path=request.background_music
        )

        job_store[job_id]["status"] = "complete"
        job_store[job_id]["output_path"] = final_path
    except Exception as e:
        job_store[job_id]["status"] = "failed"
        job_store[job_id]["error"] = str(e)

@app.get("/status/{job_id}")
def get_status(job_id: str):
    if job_id not in job_store:
        raise HTTPException(404, "Job not found")
    return {"job_id": job_id, **job_store[job_id]}
```

---

## 10. Output Specifications & Platform Formats

### Platform Requirements Matrix

| Platform | Resolution | Aspect | FPS | Max Duration | Format |
|----------|-----------|--------|-----|-------------|--------|
| TikTok | 1080x1920 | 9:16 | 30 | 10 min | H.264 MP4 |
| Instagram Reels | 1080x1920 | 9:16 | 30 | 90 sec | H.264 MP4 |
| YouTube Shorts | 1080x1920 | 9:16 | 60 | 60 sec | H.264 MP4 |
| X (Twitter) | 1280x720 | 16:9 | 30 | 2 min 20 sec | H.264 MP4 |
| Facebook Reels | 1080x1920 | 9:16 | 30 | 90 sec | H.264 MP4 |

### Processing Time Estimates

| Stage | RTX 3060 | RTX 4090 |
|-------|---------|---------|
| Edge-TTS (60s script) | 3s | 3s |
| LivePortrait (60s animation) | 4 min | 45s |
| Whisper Large-v3 | 20s | 8s |
| FFmpeg Assembly | 15s | 15s |
| **Total per video** | **~5 min** | **~1.2 min** |

---

*End of Report 03 — AI Video Production & Editing Pipeline*
