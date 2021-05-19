#!/bin/bash
#SBATCH -N 1
#SBATCH -p RM
#SBATCH -t 1:00:00
#SBATCH --ntasks-per-node=10

module load python/3.8.6
module load anaconda3
conda activate /ocean/projects/ees200007p/ah986/.conda/envs/adaptive_demands
mpirun python3 curtailment_scaling.py

