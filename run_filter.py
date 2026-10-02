"""
Local runner for m1guelpf/nsfw-filter (cog-nsfw-filter).
Uses CompVis/stable-diffusion-safety-checker + CLIP feature extractor
with the same forward_inspect patch as the original Replicate Cog model.

Defaults: threshold=0, special_threshold=0 (stock / strictest).
Default 0 = stock / strictest. 0.02 = more lenient; 0.04 = even more lenient. Higher = more lenient; lower toward 0 = stricter.
CLI: --threshold / --special-threshold (env aliases: SENSITIVITY / SPECIAL_SENSITIVITY).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from functools import partial
from pathlib import Path

import torch
from PIL import Image
from transformers import CLIPImageProcessor
from diffusers.pipelines.stable_diffusion.safety_checker import (
    StableDiffusionSafetyChecker,
)

from filter import (
    DEFAULT_THRESHOLD,
    DEFAULT_SPECIAL_THRESHOLD,
    forward_inspect,
    resolve_threshold,
    resolve_special_threshold,
)

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "diffusers-cache"


def load_models(device: str):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Loading safety checker (cache={CACHE_DIR})...", flush=True)
    safety_checker = StableDiffusionSafetyChecker.from_pretrained(
        "CompVis/stable-diffusion-safety-checker",
        cache_dir=str(CACHE_DIR),
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    ).to(device)
    safety_checker.eval()

    # Same CLIP preprocessor SD v1.5 pipelines use
    feature_extractor = CLIPImageProcessor.from_pretrained(
        "openai/clip-vit-large-patch14",
        cache_dir=str(CACHE_DIR),
    )

    safety_checker.forward = partial(forward_inspect, self=safety_checker)
    return safety_checker, feature_extractor


@torch.inference_mode()
def classify(
    image_path: Path,
    device: str,
    threshold: float | None = None,
    special_threshold: float | None = None,
    verbose: bool = False,
) -> dict:
    safety_checker, feature_extractor = load_models(device)
    image = Image.open(image_path).convert("RGB")

    safety_checker_input = feature_extractor(images=image, return_tensors="pt")
    pixel_values = safety_checker_input.pixel_values.to(device)
    if device == "cuda":
        pixel_values = pixel_values.half()

    margin = resolve_threshold(threshold)
    special_margin = resolve_special_threshold(special_threshold)
    result, has_nsfw_concepts = safety_checker.forward(
        clip_input=pixel_values,
        images=image,
        threshold=margin,
        special_threshold=special_margin,
    )

    out = {
        "nsfw_detected": bool(has_nsfw_concepts),
        "nsfw": list(result.get("nsfw", [])),
        "special": list(result.get("special", [])),
        "threshold": margin,
        "special_threshold": special_margin,
        "device": device,
        "image": str(image_path),
    }

    if verbose:
        concept_scores = result.get("concept_scores") or {}
        special_scores = result.get("special_scores") or {}
        top_concepts = sorted(concept_scores.items(), key=lambda kv: kv[1], reverse=True)[:10]
        top_special = sorted(special_scores.items(), key=lambda kv: kv[1], reverse=True)
        out["top_concept_scores"] = [
            {"concept": name, "score": score, "flagged": score > margin}
            for name, score in top_concepts
        ]
        out["special_scores"] = [
            {"concept": name, "score": score, "flagged": score > special_margin}
            for name, score in top_special
        ]
        print(f"Top concept scores (flag if score > {margin}):", flush=True)
        for row in out["top_concept_scores"]:
            mark = "FLAG" if row["flagged"] else "ok"
            print(f"  [{mark}] {row['concept']}: {row['score']}", flush=True)
        print(f"Special-care scores (flag if score > {special_margin}):", flush=True)
        for row in out["special_scores"]:
            mark = "FLAG" if row["flagged"] else "ok"
            print(f"  [{mark}] {row['concept']}: {row['score']}", flush=True)

    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local m1guelpf/nsfw-filter runner (defaults: 0 = stock / strictest; higher = more lenient)"
    )
    parser.add_argument("image", type=Path, help="Path to image to classify")
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU even if CUDA is available",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help=(
            "NSFW sensitivity (or SENSITIVITY env). Default 0 = stock / strictest. 0.02 = more lenient; 0.04 = even more lenient. Higher = more lenient; lower toward 0 = stricter."
        ),
    )
    parser.add_argument(
        "--special-threshold",
        type=float,
        default=None,
        help=(
            "Special-care sensitivity (or SPECIAL_SENSITIVITY env). Default 0 = stock / strictest. 0.02 = more lenient; 0.04 = even more lenient. Higher = more lenient; lower toward 0 = stricter."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print top concept / special-care scores for debugging",
    )
    args = parser.parse_args()

    if not args.image.is_file():
        print(f"ERROR: image not found: {args.image}", file=sys.stderr)
        return 1

    if args.cpu or not torch.cuda.is_available():
        device = "cpu"
    else:
        device = "cuda"

    margin = resolve_threshold(args.threshold)
    special_margin = resolve_special_threshold(args.special_threshold)
    print(
        f"torch={torch.__version__} cuda_available={torch.cuda.is_available()} "
        f"device={device} threshold={margin} special_threshold={special_margin} "
        f"(SENSITIVITY={os.environ.get('SENSITIVITY', '<unset>')} "
        f"SPECIAL_SENSITIVITY={os.environ.get('SPECIAL_SENSITIVITY', '<unset>')})",
        flush=True,
    )
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}", flush=True)

    out = classify(
        args.image,
        device,
        threshold=margin,
        special_threshold=special_margin,
        verbose=args.verbose,
    )
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
