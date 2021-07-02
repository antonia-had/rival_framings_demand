#!/bin/bash

module load parallel
module load anaconda3
eval "$(conda shell.bash hook)"
conda activate /ocean/projects/ees200007p/ah986/.conda/envs/adaptive_demands
python3 generate_sample_info.py