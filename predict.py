from typing import Dict, List, Optional

import torch
from PIL import Image
from functools import partial
from transformers import CLIPImageProcessor
from diffusers.pipelines.stable_diffusion.safety_checker import (
    StableDiffusionSafetyChecker,
)
from cog import BasePredictor, BaseModel, Input, Path

from filter import (
    DEFAULT_THRESHOLD,
    DEFAULT_SPECIAL_THRESHOLD,
    forward_inspect,
)

MODEL_CACHE = "diffusers-cache"
SAFETY_MODEL_ID = "CompVis/stable-diffusion-safety-checker"
FEATURE_EXTRACTOR_ID = "openai/clip-vit-large-patch14"


class FilterOutput(BaseModel):
    nsfw_detected: bool
    nsfw: List[str]
    special: List[str]
    threshold: float
    special_threshold: float
    concept_scores: Optional[Dict[str, float]] = None
    special_scores: Optional[Dict[str, float]] = None


class Predictor(BasePredictor):
    def setup(self):
        """Load CompVis safety checker + CLIP feature extractor (same as local run_filter)."""
        print("Loading safety checker...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32

        self.safety_checker = StableDiffusionSafetyChecker.from_pretrained(
            SAFETY_MODEL_ID,
            cache_dir=MODEL_CACHE,
            torch_dtype=dtype,
        ).to(self.device)
        self.safety_checker.eval()

        self.feature_extractor = CLIPImageProcessor.from_pretrained(
            FEATURE_EXTRACTOR_ID,
            cache_dir=MODEL_CACHE,
        )

        self.safety_checker.forward = partial(
            forward_inspect, self=self.safety_checker
        )
        print(f"Ready on {self.device}")

    @torch.inference_mode()
    def predict(
        self,
        image: Path = Input(
            description="Image to run through the isolated Stable Diffusion NSFW content filter.",
        ),
        threshold: float = Input(
            description=(
                "NSFW loosen margin vs stock CompVis (stock = 0, strictest). "
                "Flag when concept score exceeds this value. "
                "Higher = looser; lower toward 0 = closer to stock / stricter. "
                "Default 0.02 is intentionally looser than stock; set 0 to match stock."
            ),
            default=DEFAULT_THRESHOLD,
            ge=0.0,
            le=1.0,
        ),
        special_threshold: float = Input(
            description=(
                "Special-care loosen margin (little girl / young child / young girl). "
                "Stock CompVis = 0 (strictest). Higher = looser; lower toward 0 = closer to stock. "
                "Default 0.04 is intentionally looser than stock (not stock); set 0 to match stock."
            ),
            default=DEFAULT_SPECIAL_THRESHOLD,
            ge=0.0,
            le=1.0,
        ),
    ) -> FilterOutput:
        """Run the provided image through the NSFW filter with tunable NSFW / special-care sensitivity."""
        pil = Image.open(image).convert("RGB")
        safety_checker_input = self.feature_extractor(
            images=pil, return_tensors="pt"
        )
        pixel_values = safety_checker_input.pixel_values.to(self.device)
        if self.device == "cuda":
            pixel_values = pixel_values.half()

        result, has_nsfw_concepts = self.safety_checker.forward(
            clip_input=pixel_values,
            images=pil,
            threshold=float(threshold),
            special_threshold=float(special_threshold),
        )

        return FilterOutput(
            nsfw_detected=bool(has_nsfw_concepts),
            nsfw=list(result.get("nsfw", [])),
            special=list(result.get("special", [])),
            threshold=float(threshold),
            special_threshold=float(special_threshold),
            concept_scores=dict(result.get("concept_scores") or {}),
            special_scores=dict(result.get("special_scores") or {}),
        )
