#!/bin/bash
set -euo pipefail
export PATH="$HOME/bin:$PATH"
cd /mnt/c/Users/AIGEN/Desktop/NSFW-FILTER
cog predict -i image=@test_images/sfw_sample.png -i threshold=0.02 -i special_threshold=0.04