# Stable Diffusion NSFW Filter

<p align="center"><b><a href="https://replicate.com/m1guelpf/nsfw-filter" target="_blank">View original on Replicate</a> | <a href="https://github.com/m1guelpf/cog-nsfw-filter" target="_blank">Upstream repo</a></b></p>

An isolated version of Stable Diffusion's content filter, which lets you run it against arbitrary images.

This fork of [m1guelpf/cog-nsfw-filter](https://github.com/m1guelpf/cog-nsfw-filter) contains a modified implementation of the example code from the [Red-Teaming the Stable Diffusion Safety Filter](https://arxiv.org/abs/2210.04610v5) paper. It uses the CompVis safety checker only (no full Stable Diffusion pipeline).

## Sensitivity (threshold / special_threshold)

Stock CompVis Stable Diffusion safety checker flags when a concept score is **> 0**. That is the strictest / original behavior.

**This project's defaults match stock:** `threshold=0` and `special_threshold=0`.

| Input | Default | Meaning |
|-------|---------|---------|
| `threshold` | `0` | NSFW loosen margin. Flag when concept score exceeds this value. `0` = stock CompVis (strictest). Higher = looser (e.g. `0.02`). |
| `special_threshold` | `0` | Special-care loosen margin (`little girl`, `young child`, `young girl`). `0` = stock CompVis (strictest). Higher = looser (e.g. `0.04`). |

**Rule of thumb:** higher = looser (fewer flags); lower toward `0` = closer to stock / stricter. Defaults already match stock; raise the values only if you want a looser filter.

Local CLI uses the same knobs via `--threshold` / `--special-threshold` (or `SENSITIVITY` / `SPECIAL_SENSITIVITY` env vars).

## Development

> **Note** If you just wanna try the upstream model out or run it in production, see the Replicate link above.

This model is packaged as a [Cog](https://github.com/replicate/cog) model, a tool to package machine learning models as standard containers.

First, [download Cog](https://github.com/replicate/cog#install) on your system. Then download the pre-trained weights:

```bash
cog run script/download-weights
```

Once set up, you can run predictions (sample image included as `example.jpg`):

```bash
cog predict -i image=@example.jpg
```

Stock-default result shape:

```json
{
  "nsfw_detected": false,
  "nsfw": [],
  "special": [],
  "threshold": 0.0,
  "special_threshold": 0.0
}
```

Looser example (optional — not the defaults):

```bash
cog predict -i image=@example.jpg -i threshold=0.02 -i special_threshold=0.04
```

### Local runner (no Cog required)

```bash
python run_filter.py example.jpg
python run_filter.py example.jpg --threshold 0.02 --special-threshold 0.04
python run_filter.py example.jpg --threshold 0.03 --special-threshold 0.05 --verbose
```

### Push to Replicate

Do **not** push to `m1guelpf/nsfw-filter`. Create a new model under your own account:

```bash
cog login
cog push r8.im/<YOUR_USERNAME>/nsfw-filter-adjustable
```
