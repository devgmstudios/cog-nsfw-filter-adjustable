#!/bin/bash
set -euo pipefail
export PATH="$HOME/bin:$PATH"
# Run from the repo root
cog predict -i image=@example.jpg -i threshold=0.02 -i special_threshold=0.04
