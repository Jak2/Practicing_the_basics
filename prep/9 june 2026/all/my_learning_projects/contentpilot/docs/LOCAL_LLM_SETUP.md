# Local LLM Setup — ContentPilot

> Why this exists: The Gemini free tier has daily request limits. Once you hit them, the agent
> fails with a `429 RESOURCE_EXHAUSTED` error. This guide sets up a local LLM (running on your
> own machine, no internet required, no API key needed) as the text generation backend.

---

## Hardware This Was Configured For

| Component | Spec |
|---|---|
| CPU | Intel i5-11400H, 6 cores / 12 threads @ 2.70GHz |
| RAM | 7.5GB total (approx 900MB free during normal use) |
| GPU | NVIDIA GTX 1650 Mobile — **4GB VRAM** (CUDA 13.2) |
| OS | Linux (Ubuntu-based) |

> The model runs on the GPU (VRAM), not RAM. That's why it works even with low free RAM.
> The GPU handles all the heavy compute via CUDA.

---

## What Is Ollama?

Ollama is a tool that lets you download and run open-source LLMs on your own computer.
It works like this:

```
your code (Python / LangChain)
        ↓
Ollama server (running in background on localhost:11434)
        ↓
LLM model (phi3:mini, loaded into GPU VRAM)
        ↓
response returned to your code
```

You don't need an API key. The model runs entirely on your machine.

---

## Chosen Model: `phi3:mini`

**Why this model for this machine:**

| Requirement | Why phi3:mini fits |
|---|---|
| Fits in 4GB VRAM | Uses ~2.2GB — leaves room for the OS and GPU driver overhead |
| Good at structured output | Follows YAML frontmatter + markdown format reliably |
| Fast enough on GTX 1650 | ~15–30 tokens/sec — a full post takes 20–60 seconds |
| No internet needed after download | Model runs fully offline once pulled |

**Other models you could use (all fit in 4GB VRAM):**

| Model | VRAM | Speed | Quality | Best For |
|---|---|---|---|---|
| `phi3:mini` | ~2.2GB | Medium | ★★★★ | Structured output, following instructions |
| `llama3.2:3b` | ~2.0GB | Fast | ★★★★ | General writing, natural tone |
| `gemma2:2b` | ~1.6GB | Very fast | ★★★ | Quick drafts, low RAM pressure |
| `qwen2.5:3b` | ~2.0GB | Medium | ★★★★ | Multilingual, structured formats |
| `tinyllama` | ~0.6GB | Very fast | ★★ | Testing only — quality is low |

> **Do NOT try models larger than 7B** on this machine. A 7B model needs ~4GB VRAM minimum,
> which leaves zero headroom and will either crash or fall back to slow CPU inference.

---

## Installation Steps

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

After installation, Ollama runs as a background service automatically on boot.
You can check it's running with:

```bash
ollama list        # lists downloaded models
ollama ps          # shows currently loaded model
```

### 2. Pull the model

```bash
ollama pull phi3:mini
```

This downloads ~2.2GB. Only needed once — the model is cached on disk after that.

### 3. Verify it works

```bash
ollama run phi3:mini "Write a one-paragraph summary of machine learning"
# Should print a paragraph. Press Ctrl+D to exit the interactive mode.
```

### 4. Install the LangChain Ollama package

```bash
cd my_learning_projects/contentpilot
source .venv/bin/activate.fish
pip install langchain-ollama
```

This is already added to `requirements.txt` so future `pip install -r requirements.txt` will include it.

---

## How ContentPilot Uses the Local LLM

### Configuration (`config.yaml`)

```yaml
llm:
  provider: ollama          # switch between "ollama" (local) and "google" (Gemini API)
  model: phi3:mini          # which Ollama model to use
  # model: gemini-2.0-flash # uncomment this line if switching back to Google
  image_model: imagen-3.0-generate-001  # only used when provider is "google"
```

**To switch back to Gemini** (when you have quota again):

```yaml
llm:
  provider: google
  model: gemini-2.0-flash
  image_model: imagen-3.0-generate-001
```

### How the code switches providers (`agents/content_generator.py`)

```python
class ContentGenerator:
    def __init__(self, config: Config):
        if config.llm.provider == "ollama":
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(model=config.llm.model, temperature=0.7)
        else:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=config.llm.model,
                google_api_key=os.getenv("GEMINI_API_KEY", ""),
            )
```

The rest of `content_generator.py` doesn't change — both providers use the same LangChain
`.invoke()` interface. This is the benefit of using LangChain as an abstraction layer.

---

## What Works and What Doesn't with Local LLM

| Feature | With Ollama | Notes |
|---|---|---|
| Fetching trends (HackerNews) | ✅ Works | No LLM involved — pure HTTP |
| Generating prompt posts | ✅ Works | phi3:mini follows the markdown format well |
| Generating workflow posts | ✅ Works | Same as above |
| Image generation | ❌ Not available | Imagen is a Google API — no local equivalent set up |
| Git commit + push | ✅ Works | No LLM involved — pure GitPython |
| Dashboard | ✅ Works | No LLM involved — reads manifest.json |

**Image generation with local LLM:**

When `provider: ollama`, image generation will fail for every prompt post (the error is caught
and logged — the post still publishes, just without an image). You'll see this in the
`/pipeline` page as a red `ImageGenerator.run()` step.

**To avoid image generation errors entirely:**

When running `python main.py`, set prompts per topic to `0`:

```
Prompts per topic (with image): 0
Workflows per topic: 2
```

Workflow posts never generate images, so the run will be fully local.

---

## Performance Expectations

On this machine (GTX 1650, 4GB VRAM), generating one post with phi3:mini takes:

| Post type | Approx time |
|---|---|
| Workflow post (4 steps, ~400 words) | 30–60 seconds |
| Prompt post (150–300 words) | 15–30 seconds |

This is slower than the Gemini API (~3–8 seconds per post), but it's free, offline, and not
rate-limited.

---

## Troubleshooting

### "Connection refused" when running main.py

Ollama server isn't running. Start it manually:

```bash
ollama serve
```

Or check if the service is active:

```bash
systemctl status ollama
```

### Model response doesn't follow the markdown format

phi3:mini can occasionally drift from the exact format. The post will still be published
but the YAML frontmatter might be slightly off. If this happens consistently, try:

```bash
ollama pull llama3.2:3b    # pull an alternative
```

Then update `config.yaml`:

```yaml
llm:
  model: llama3.2:3b
```

### "CUDA out of memory" error

Another process is using your GPU. Check what's using VRAM:

```bash
nvidia-smi
```

Close any GPU-heavy apps (games, video editors) and try again.

### GPU not being used (inference is very slow)

Check if Ollama is using CUDA:

```bash
ollama ps
# Should show the model with "GPU" listed
```

If it shows "CPU", your CUDA setup may need fixing:

```bash
nvidia-smi    # check driver is loaded
nvcc --version    # check CUDA toolkit
```

---

## Switching Between Local and Cloud

You only need to change one line in `config.yaml`:

```yaml
# Local (no cost, no internet needed, slower):
provider: ollama
model: phi3:mini

# Cloud (fast, needs API key, has daily quota):
provider: google
model: gemini-2.0-flash
```

No code changes needed. Restart `python main.py` after changing the config.

---

## Future: Local Image Generation

Getting local image generation working on 4GB VRAM is possible but requires a separate setup:

- **Tool needed:** [Stable Diffusion via ComfyUI or Automatic1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- **Model that fits:** Stable Diffusion 1.5 (~2GB VRAM) or SDXL Turbo (~4GB VRAM, tight)
- **Integration:** ContentPilot's `ImageGenerator` class would need a new provider branch
  pointing at the ComfyUI API (it runs a local HTTP server similar to Ollama)
- **Effort:** Medium — 1–2 days to set up ComfyUI + wire it into ContentPilot

This is noted as a future improvement but not currently implemented.
