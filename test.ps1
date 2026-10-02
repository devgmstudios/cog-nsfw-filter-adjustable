# Quick smoke test for local nsfw-filter
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$img = Join-Path $PSScriptRoot "test_images\sfw_sample.png"
if (-not (Test-Path $img)) {
    Write-Error "Missing test image: $img — create it first or pass another path."
}
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\run_filter.py" $img
