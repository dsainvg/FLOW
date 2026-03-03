#!/bin/bash
while true; do
  if [ -f outputs/flow_9x9_10000.npz ]; then
    git add outputs/*.npz
    git commit -m "Upload massive datasets"
    break
  fi
  sleep 60
done
