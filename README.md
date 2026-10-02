# Stable Diffusion NSFW Filter

<p align="center"><b><a href="https://github.com/devgmstudios/cog-nsfw-filter-adjustable" target="_blank">GitHub</a> | <a href="https://replicate.com/devgmstudios/nsfw-filter-adjustable" target="_blank">View on Replicate</a> | <a href="https://github.com/m1guelpf/cog-nsfw-filter" target="_blank">Upstream</a></b></p>

An isolated version of Stable Diffusion's content filter, which lets you run it against arbitrary images.

This fork of [m1guelpf/cog-nsfw-filter](https://github.com/m1guelpf/cog-nsfw-filter) contains a modified implementation of the example code from the [Red-Teaming the Stable Diffusion Safety Filter](https://arxiv.org/abs/2210.04610v5) paper. It uses the CompVis safety checker only (no full Stable Diffusion pipeline).

## Sensitivity adjustment

Stock CompVis behavior uses `threshold=0` and `special_threshold=0` — that is the **most aggressive** setting (flags the most).

- **Lower threshold (toward 0)** = **more aggressive** (more flags). `0` is stock / strictest.
- **Higher threshold** = **less aggressive** (fewer flags). Try `0.02` or `0.04` for a more lenient filter.

| Input | Default | Meaning |
|-------|---------|---------|
| `threshold` | `0` | NSFW sensitivity. Flag when concept score exceeds this value. |
| `special_threshold` | `0` | Special-care sensitivity. Same scale as `threshold`. |

## Development

> **Note** To try the model or run it in production, use the Replicate link above.

Packaged with [Cog](https://github.com/replicate/cog). Clone this repo, then:

```bash
cog run script/download-weights
cog predict -i image=https://st2.depositphotos.com/1001001/9140/i/950/depositphotos_91408974-stock-photo-little-girl-on-vacation.jpg
```

Push (own account only — do not push to `m1guelpf/nsfw-filter`):

```bash
cog push r8.im/devgmstudios/nsfw-filter-adjustable
```
