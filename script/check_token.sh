#!/bin/bash
export PATH="$HOME/bin:$PATH"
if [ -n "${REPLICATE_API_TOKEN+x}" ]; then echo DECLARED=yes; else echo DECLARED=no; fi
if [ -n "${REPLICATE_API_TOKEN:-}" ]; then echo NONEMPTY=yes len=${#REPLICATE_API_TOKEN}; else echo NONEMPTY=no; fi
env | grep -i replicate || echo NO_REPLICATE_IN_ENV
env | grep -i cog || echo NO_COG_IN_ENV