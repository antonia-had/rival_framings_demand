#!/bin/bash

start_vals=($(seq 1 50 551))
end_vals=($(seq 50 50 600))
batches=($(seq 1 12))

for i in "${!batches[@]}"; do
  sbatch --job-name=batch_${batches[$i]} \
  --output=./outputs/batch_${batches[$i]}.out \
  --error=./errors/batch_${batches[$i]}.err \
  curtailment_scaling_comet.sh ${start_vals[$i]} ${end_vals[$i]} ${batches[$i]}
  sleep 0.5
done