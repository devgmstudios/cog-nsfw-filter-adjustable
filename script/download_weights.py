"""Pre-download CompVis safety checker + CLIP feature extractor into MODEL_CACHE for Cog image bake-in."""
from pathlib import Path

from transformers import CLIPImageProcessor
from diffusers.pipelines.stable_diffusion.safety_checker import (
    StableDiffusionSafetyChecker,
)

MODEL_CACHE = Path("diffusers-cache")
SAFETY_MODEL_ID = "CompVis/stable-diffusion-safety-checker"
FEATURE_EXTRACTOR_ID = "openai/clip-vit-large-patch14"


def main() -> None:
    MODEL_CACHE.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SAFETY_MODEL_ID} -> {MODEL_CACHE}")
    StableDiffusionSafetyChecker.from_pretrained(
        SAFETY_MODEL_ID,
        cache_dir=str(MODEL_CACHE),
    )
    print(f"Downloading {FEATURE_EXTRACTOR_ID} -> {MODEL_CACHE}")
    CLIPImageProcessor.from_pretrained(
        FEATURE_EXTRACTOR_ID,
        cache_dir=str(MODEL_CACHE),
    )
    print("Weights ready.")


if __name__ == "__main__":
    main()
