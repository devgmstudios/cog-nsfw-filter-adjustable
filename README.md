# Stable Diffusion NSFW Filter (adjustable)

An isolated version of Stable Diffusion's content filter, which lets you run it against arbitrary images.

This fork of [m1guelpf/cog-nsfw-filter](https://github.com/m1guelpf/cog-nsfw-filter) (Replicate: [m1guelpf/nsfw-filter](https://replicate.com/m1guelpf/nsfw-filter)) uses the CompVis safety checker only (no full Stable Diffusion pipeline) and exposes **adjustable thresholds** so you can tune how aggressive the filter is.

**Try / view:** [m1guelpf/nsfw-filter on Replicate](https://replicate.com/m1guelpf/nsfw-filter) (original) | deploy this adjustable build under your own Replicate account (see below).

## Adjustable thresholds

Stock Stable Diffusion flags when `(cosine - concept_threshold + adjustment) > 0`. This runner defaults to requiring more headroom:

| Input | Default | Meaning |
|-------|---------|---------|
| `threshold` | `0.02` | NSFW concept loosen margin. Higher = less aggressive. `0` = stock SD. |
| `special_threshold` | `0.04` | Special-care concepts (`little girl`, `young child`, `young girl`). Higher = less aggressive. `0` = stock. |

Local CLI mirrors the same knobs via `--threshold` / `--special-threshold` (or `SENSITIVITY` / `SPECIAL_SENSITIVITY` env vars).

## Example

Sample image included in this repo:

`depositphotos_196583668-stock-photo-mother-daughter-walking-run-beautiful.jpg`

**Local (Windows):**

```powershell
.\.venv\Scripts\python.exe run_filter.py .\depositphotos_196583668-stock-photo-mother-daughter-walking-run-beautiful.jpg
```

**Cog (WSL + Docker Desktop):**

```bash
export PATH="$HOME/bin:$PATH"
cd /mnt/c/Users/AIGEN/Desktop/NSFW-FILTER
cog predict -i image=@depositphotos_196583668-stock-photo-mother-daughter-walking-run-beautiful.jpg -i threshold=0.02 -i special_threshold=0.04
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

## Local usage (Windows, no Cog required)

Uses the Stable Diffusion safety checker (`CompVis/stable-diffusion-safety-checker`) with the same `forward_inspect` patch from `filter.py`. Full Cog/Docker is not required for the local runner.

### Sensitivity examples

```powershell
# defaults (NSFW 0.02, special-care 0.04)
.\.venv\Scripts\python.exe run_filter.py .\test_images\sfw_sample.png

# stock SD aggressiveness for both
.\.venv\Scripts\python.exe run_filter.py .\img.png --threshold 0 --special-threshold 0

# a bit looser still on NSFW
.\.venv\Scripts\python.exe run_filter.py .\img.png --threshold 0.03

# tune special-care only
.\.venv\Scripts\python.exe run_filter.py .\img.png --special-threshold 0.05

# via env
$env:SENSITIVITY = "0.025"
$env:SPECIAL_SENSITIVITY = "0.04"
.\.venv\Scripts\python.exe run_filter.py .\img.png

# debug: print top concept / special-care scores
.\.venv\Scripts\python.exe run_filter.py .\img.png --verbose
```

### Setup

```powershell
cd $env:USERPROFILE\Desktop\NSFW-FILTER
.\.venv\Scripts\Activate.ps1
```

### Run

```powershell
cd $env:USERPROFILE\Desktop\NSFW-FILTER
.\.venv\Scripts\Activate.ps1
python run_filter.py path\to\image.jpg
```

Or without activating:

```powershell
.\.venv\Scripts\python.exe run_filter.py .\test_images\sfw_sample.png
```

Quick test script:

```powershell
.\test.ps1
```

### Output JSON

```json
{
  "nsfw_detected": false,
  "nsfw": [],
  "special": [],
  "threshold": 0.02,
  "special_threshold": 0.04,
  "device": "cuda",
  "image": "..."
}
```

- `nsfw_detected` — true if any NSFW concept score exceeds the (possibly loosened) threshold
- `nsfw` — matched concept names (sexual, nude, …)
- `special` — matched special-care concepts (little girl, young child, young girl)
- `threshold` — NSFW loosen margin in use (0 = stock)
- `special_threshold` — special-care loosen margin in use (0 = stock)

With `--verbose`, also prints top concept / special-care scores and includes them in the JSON.

Weights cache: `diffusers-cache\` (Hugging Face hub layout).

## Replicate / Cog deploy

Cog model inputs:

- `image` (required) — image to classify
- `threshold` (float, default `0.02`) — NSFW concept loosen margin
- `special_threshold` (float, default `0.04`) — special-care loosen margin

Outputs: `nsfw_detected`, `nsfw`, `special`, `threshold`, `special_threshold`, `concept_scores`, `special_scores`.

### Local Cog test (WSL + Docker Desktop)

```bash
export PATH="$HOME/bin:$PATH"
cd /mnt/c/Users/AIGEN/Desktop/NSFW-FILTER
cog predict -i image=@test_images/sfw_sample.png -i threshold=0.02 -i special_threshold=0.04
```

### Push to Replicate (new model under your account)

Do **not** force-push to `m1guelpf/cog-nsfw-filter`. Create a **new** GitHub repo (e.g. `cog-nsfw-filter-adjustable`) and a new Replicate model slug under your account:

```bash
export REPLICATE_API_TOKEN=r8_...
export PATH="$HOME/bin:$PATH"
cd /mnt/c/Users/AIGEN/Desktop/NSFW-FILTER
cog login
cog push r8.im/<YOUR_USERNAME>/nsfw-filter-adjustable
```

Then the model URL is `https://replicate.com/<YOUR_USERNAME>/nsfw-filter-adjustable`.