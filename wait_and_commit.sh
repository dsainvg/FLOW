#!/bin/bash
while true; do
  if [ -f outputs/flow_9x9_10000.npz ] && [ -f outputs/flow_4x4_1000.npz ]; then
    git add outputs/*.npz
    git commit -m "Add final generated exact 4x4 (1000) and 9x9 (10000) output npz files"
    break
  fi
  sleep 60
done
