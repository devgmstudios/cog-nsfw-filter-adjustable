import os
import torch
from torch import nn

# Stable Diffusion NSFW filter config (see LAION-AI/CLIP-based-NSFW-Detector repo).
concepts = ['sexual', 'nude', 'sex', '18+', 'naked', 'nsfw', 'porn', 'dick', 'vagina',
            'naked child', 'explicit content', 'uncensored', 'fuck', 'nipples', 'visible nipples', 'naked breasts', 'areola']
special_concepts = ["little girl", "young child", "young girl"]

# Default loosen vs stock SD checker: require this much extra headroom before flagging NSFW.
# Stock flags when (cosine - concept_threshold + adjustment) > 0.
# With DEFAULT_THRESHOLD=0.02, flags when that score > 0.02 (~0.02 less aggressive).
DEFAULT_THRESHOLD = 0.02
# Special-care concepts: same style as NSFW, default score > 0.04 (less aggressive than stock > 0).
DEFAULT_SPECIAL_THRESHOLD = 0.04


def cosine_distance(image_embeds, text_embeds):
    normalized_image_embeds = nn.functional.normalize(image_embeds)
    normalized_text_embeds = nn.functional.normalize(text_embeds)
    return torch.mm(normalized_image_embeds, normalized_text_embeds.t())


def resolve_threshold(threshold=None):
    """Resolve NSFW loosen margin: explicit arg > SENSITIVITY env > DEFAULT_THRESHOLD.
    Higher value = less aggressive (harder to flag NSFW). Use 0 for stock SD behavior.
    """
    if threshold is not None:
        return float(threshold)
    env = os.environ.get("SENSITIVITY")
    if env is not None and env.strip() != "":
        return float(env)
    return DEFAULT_THRESHOLD


def resolve_special_threshold(threshold=None):
    """Resolve special-care margin: explicit arg > SPECIAL_SENSITIVITY env > DEFAULT_SPECIAL_THRESHOLD.
    Higher value = less aggressive. Use 0 for stock SD behavior (score > 0).
    """
    if threshold is not None:
        return float(threshold)
    env = os.environ.get("SPECIAL_SENSITIVITY")
    if env is not None and env.strip() != "":
        return float(env)
    return DEFAULT_SPECIAL_THRESHOLD


@torch.no_grad()
def forward_inspect(self, clip_input, images, threshold=None, special_threshold=None):
    """Inspect CLIP embeds against NSFW + special-care concepts.

    threshold: NSFW margin above stock (default ~0.02). Higher = less aggressive.
    special_threshold: special-care margin (default ~0.04). Higher = less aggressive.
    """
    margin = resolve_threshold(threshold)
    special_margin = resolve_special_threshold(special_threshold)

    pooled_output = self.vision_model(clip_input)[1]
    image_embeds = self.visual_projection(pooled_output)

    special_cos_dist = cosine_distance(
        image_embeds, self.special_care_embeds
    ).cpu().numpy()
    cos_dist = cosine_distance(image_embeds, self.concept_embeds).cpu().numpy()

    matches = {
        "nsfw": [],
        "special": [],
        "concept_scores": {},
        "special_scores": {},
        "threshold": margin,
        "special_threshold": special_margin,
    }
    batch_size = image_embeds.shape[0]
    for i in range(batch_size):
        result_img = {
            "special_scores": {}, "special_care": [], "concept_scores": {}, "bad_concepts": []
        }

        adjustment = 0.0

        # Special-care: require score > special_margin (default 0.04).
        for concet_idx in range(len(special_cos_dist[0])):
            concept_cos = special_cos_dist[i][concet_idx]
            concept_threshold = self.special_care_embeds_weights[concet_idx].item()
            score = float(round(float(concept_cos) - concept_threshold + adjustment, 3))
            name = special_concepts[concet_idx]
            result_img["special_scores"][concet_idx] = score
            matches["special_scores"][name] = score
            if score > special_margin:
                result_img["special_care"].append(
                    {concet_idx, score}
                )
                adjustment = 0.01
                matches["special"].append(name)

        # NSFW concepts: require score > margin (default 0.02) instead of stock > 0.
        for concet_idx in range(len(cos_dist[0])):
            concept_cos = cos_dist[i][concet_idx]
            concept_threshold = self.concept_embeds_weights[concet_idx].item()
            score = float(round(float(concept_cos) - concept_threshold + adjustment, 3))
            name = concepts[concet_idx]
            result_img["concept_scores"][concet_idx] = score
            matches["concept_scores"][name] = score

            if score > margin:
                result_img["bad_concepts"].append(concet_idx)
                matches["nsfw"].append(name)

    has_nsfw_concepts = len(matches["nsfw"]) > 0

    return matches, has_nsfw_concepts
