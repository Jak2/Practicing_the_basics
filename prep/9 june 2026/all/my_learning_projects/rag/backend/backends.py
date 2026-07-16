"""Swappable backend factories: embedders and LLMs. Selected via config."""


# ---- Embedders ----
class LocalEmbedder:
    def __init__(self, model="BAAI/bge-small-en-v1.5"):
        from sentence_transformers import SentenceTransformer
        self._m = SentenceTransformer(model)
        self.name = f"local:{model}"

    def embed(self, texts):
        return self._m.encode(texts, normalize_embeddings=True).tolist()


def get_embedder(cfg):
    kind = cfg["embed"]
    if kind == "local":
        return LocalEmbedder()
    raise ValueError(f"unknown embed backend: {kind}")  # ponytail: add openai/voyage when needed


# ---- LLMs ----
class ClaudeLLM:
    def __init__(self):
        import anthropic
        self._c = anthropic.Anthropic()
        self.name = "claude:claude-opus-4-8"

    def answer(self, question, context):
        with self._c.messages.stream(
            model="claude-opus-4-8",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=(
                "Answer the question using ONLY the provided context. "
                "Cite the source file for each claim like [source: filename]. "
                "If the context does not contain the answer, say so plainly."
            ),
            messages=[{"role": "user",
                       "content": f"<context>\n{context}\n</context>\n\nQuestion: {question}"}],
        ) as s:
            return "".join(b.text for b in s.get_final_message().content if b.type == "text")


class OllamaLLM:
    def __init__(self, model="qwen2.5:1.5b"):
        import ollama
        self._ollama = ollama
        self._model = model
        self.name = f"ollama:{model}"

    def answer(self, question, context):
        r = self._ollama.chat(model=self._model, messages=[
            {"role": "system", "content": "Answer using ONLY the context. Cite source files like [source: filename]. If not answerable from context, say so."},
            {"role": "user", "content": f"<context>\n{context}\n</context>\n\nQuestion: {question}"},
        ])
        return r["message"]["content"]


def get_llm(cfg):
    kind = cfg["llm"]
    if kind == "claude":
        return ClaudeLLM()
    if kind == "ollama":
        return OllamaLLM(cfg.get("ollama_model", "llama3.1"))
    raise ValueError(f"unknown llm backend: {kind}")  # ponytail: add openai-compatible when needed
