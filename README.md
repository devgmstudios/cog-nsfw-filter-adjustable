# Stable Diffusion NSFW Filter (adjustable)

<p align="center"><b><a href="https://replicate.com/m1guelpf/nsfw-filter" target="_blank">View original on Replicate</a> | <a href="https://github.com/m1guelpf/cog-nsfw-filter" target="_blank">Upstream repo</a></b></p>

An isolated version of Stable Diffusion's content filter, which lets you run it against arbitrary images - with **adjustable thresholds**.

This fork of [m1guelpf/cog-nsfw-filter](https://github.com/m1guelpf/cog-nsfw-filter) contains a modified implementation of the example code from the [Red-Teaming the Stable Diffusion Safety Filter](https://arxiv.org/abs/2210.04610v5) paper. It uses the CompVis safety checker only (no full Stable Diffusion pipeline) and exposes loosen margins so you can tune how aggressive the filter is.

## Adjustable thresholds

Stock Stable Diffusion flags when `(cosine - concept_threshold + adjustment) > 0`. This runner defaults to requiring more headroom:

| Input | Default | Meaning |
|-------|---------|---------|
| `threshold` | `0.02` | NSFW concept loosen margin. Higher = less aggressive. `0` = stock SD. |
| `special_threshold` | `0.04` | Special-care concepts (`little girl`, `young child`, `young girl`). Higher = less aggressive. `0` = stock. |

Local CLI mirrors the same knobs via `--threshold` / `--special-threshold` (or `SENSITIVITY` / `SPECIAL_SENSITIVITY` env vars).

## Development

> **Note** If you just wanna try the upstream model out or run it in production, see the Replicate link above.

This model is packaged as a [Cog](https://github.com/replicate/cog) model, a tool to package machine learning models as standard containers.

First, [download Cog](https://github.com/replicate/cog#install) on your system. Then download the pre-trained weights:

```bash
cog run script/download-weights
```

Once set up, you can run predictions (sample image included as `example.jpg`):

```bash
cog predict -i image=@example.jpg -i threshold=0.02 -i special_threshold=0.04
```

Typical SFW result shape:

```json
{
  "nsfw_detected": false,
  "nsfw": [],
  "special": [],
  "threshold": 0.02,
  "special_threshold": 0.04
}
```

### Local runner (no Cog required)

```bash
python run_filter.py example.jpg
python run_filter.py example.jpg --threshold 0 --special-threshold 0
python run_filter.py example.jpg --threshold 0.03 --special-threshold 0.05 --verbose
```

### Push to Replicate

Do **not** push to `m1guelpf/nsfw-filter`. Create a new model under your own account:

```bash
cog login
cog push r8.im/<YOUR_USERNAME>/nsfw-filter-adjustable
```
