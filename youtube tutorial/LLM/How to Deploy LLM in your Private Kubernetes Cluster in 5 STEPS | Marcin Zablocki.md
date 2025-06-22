>https://www.youtube.com/watch?v=0xLGkMyXheI

# Deploy Large Language Models on Your Private Kubernetes Cluster in 5 Steps! 🤖

Hi, I’m Martin Zaboski, MLOps architect at Getting Data. Today, I’ll walk you through deploying large language models (LLMs) like Mistral on your private Kubernetes cluster in just five steps. **This video follows a July blog post where I deployed Falcon using Hugging Face’s TGI, but since then, TGI’s license got restrictive, and open-source LLM rankings shifted—Mistral 7B is now a top pick.** Let’s dive in!

---

## Intro & Context (0:00) 🌐  
**Context**: **This tutorial updates a July blog post, adapting to changes like TGI’s restrictive license and the rise of new LLM deployment frameworks. I’ll use vLLM, an Apache 2.0-licensed, fast, open-source option for private or commercial use.**  
- **Goal**: Deploy Mistral 7B on Kubernetes, scalable across AWS, GCP, Azure, or on-premise setups using standard resources.  
- **Note**: The approach uses GCS (or S3/Azure equivalents), persistent volumes, deployments, services, and batch jobs—universal Kubernetes features.

---

## Why This Setup? (2:00) 💡  
**Context**: **The design aims for scalability as your usage and customer base grow, requiring more replicas. Each container needs model file access, solved by GCS and PVC for efficiency.**  
- **Old Way**: Downloading model files from GCS per container was slow due to network reliance.  
- **New Way**: **Initialize a persistent volume once, then attach it to all deployments for faster startup.**  
- **Tip**: **Use separate volumes per zone or regional storage (e.g., EFS) to avoid zone-bound access issues when scaling.**

---

## STEP 1: Download the Model from Hugging Face (4:18) 📥  
**Context**: **Start by grabbing your model from Hugging Face—I’m using Mistral 7B Instruct 0.2. Ensure your GPU can handle it.**  
- **How**:  
  - Go to the Hugging Face Hub, find Mistral 7B, and hit the “Files” tab.  
  - Download “safetensors” files (not pickle/pytorch)—copy to GCS, S3, or Azure blob storage.  
- **Note**: **Keep the bucket/storage in the same region as your Kubernetes cluster for faster transfers.**  
- **Status**: I’ve uploaded Mistral files to GCS—ready for the next step!

---

## STEP 2: Persistent Volume (6:58) 💾  
**Context**: **Create a persistent volume claim (PVC) to store model files, retaining them across crashes.**  
- **Setup**:  
  - Use the same storage class with a “retain” reclaim policy.  
  - Assign enough storage for your model (e.g., Mistral 7B).  
  - Run `kubectl apply` to create it.  
- **Key Points**: **Set allowed topologies to match GPU availability due to shortages—verify region/zone alignment.**  
- **Check**: Volume’s created—next, copy files.

---

## STEP 3: Copy the Model Files from Blob Storage into the Persistent Volume (7:37) 🔄  
**Context**: **Use a batch job to transfer files from GCS to the PVC, ensuring correct node selection.**  
- **How**:  
  - Create a job with `gcloud SDK` (or AWS CLI/Azure equivalent) targeting your zone (e.g., Europe West 4-c).  
  - Mount the PVC at `/local/model` and copy files from GCS.  
  - Run `kubectl create` and check with `kubectl get jobs`.  
- **Status**: One job ran; another’s pending—waiting a bit.

---

## STEP 4: Deploy the LLM using vLLM (9:03) 🚀  
**Context**: **This is the core step—deploying Mistral 7B with vLLM, scalable via replicas or autoscalers.**  
- **Deployment**:  
  - Start with 2 replicas (scale up in production with HPA or KEDA).  
  - Use node selectors for GPU access (e.g., Nvidia L4 in Europe West 4-c).  
  - Mount the PVC read-only to all replicas for quick starts.  
- **Container**:  
  - Run vLLM from Docker Hub (or a private registry for isolation).  
  - Expose the model as an OpenAI-compatible HTTP API on port 8000.  
- **Resources**: Request 7 CPUs, 32GB memory, 1 Nvidia L4 GPU—suitable for Mistral 7B in BF16.  
- **Apply**: Run `kubectl apply`—deployment’s live!

---

## STEP 5: Querying the Model (13:19) 🔍  
**Context**: **The model’s running—let’s test it with API calls.**  
- **Setup**:  
  - Create a cluster IP service for port 8000.  
  - Port-forward local port 8000 to the service.  
- **Request Format**:  
  - Specify model, prompt, max tokens, temperature (lower for stability).  
  - Use `<|startoftext|><|im_start|>instruction<|im_end|>` for Mistral 7B.  
  - Get model ID from `/v1/models` JSON endpoint.  
- **Test**:  
  - Query: “Who is James Hatfield?” → “Lead singer, guitarist of Metallica.”  
  - Extract challenges from a blog: Ran a script, got concise results.  
- **Use Case**: Chat, summarize, or augment workflows in your private setup.

---

## Conclusion 🎉  
You’ve deployed Mistral 7B on your Kubernetes cluster in five steps! **Thumbs up, subscribe, and check our blog for more. Want free MLOps consultation? Hit the form below.** See you next time—bye!

---

### Optimization Check ✅  
- **Context Preserved**: Kept Martin’s tone, July blog reference, and tool shifts (TGI to vLLM).  
- **Highlighting**: Bolded key context (license changes, scalability, GPU setup) and intent (step-by-step guidance).  
- **SEO**: Targets "deploy LLM 2025," "Kubernetes LLM tutorial," and "MLOps tips" for reach.  
- **Readability**: Concise, with emojis and his style intact.  

Optimized as of 02:59 AM IST, June 23, 2025. Feedback welcome!
