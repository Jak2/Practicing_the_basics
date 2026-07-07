import os
from pathlib import Path
import google.genai as genai
from google.genai import types as genai_types
from core.config import Config


class ImageGenerator:
    def __init__(self, config: Config):
        self.config = config
        self._client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))

    def run(self, topic_title: str, slug: str, target_repo: str) -> str:
        prompt = (
            f"High-quality digital illustration representing: {topic_title}. "
            "Modern, minimal, professional style. No text overlays."
        )
        response = self._client.models.generate_images(
            model=self.config.llm.image_model,
            prompt=prompt,
            config=genai_types.GenerateImagesConfig(number_of_images=1),
        )
        image_bytes = response.generated_images[0].image.image_bytes

        rel_path = self.config.content_paths.images
        abs_dir = Path(target_repo) / rel_path
        abs_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{slug}.png"
        (abs_dir / filename).write_bytes(image_bytes)

        return f"{rel_path}/{filename}"
