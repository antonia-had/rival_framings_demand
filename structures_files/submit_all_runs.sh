#!/bin/bash

start_vals=($(seq 1 50 551))
end_vals=($(seq 50 50 600))
batches=($(seq 1 12))

for i in "${!batches[@]}"; do
  echo "Submitting samples ${start_vals[$i]} to ${end_vals[$i]}"
done