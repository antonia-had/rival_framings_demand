#!/bin/bash

# SBATCH --nodes=1
# SBATCH --ntasks=20
# SBATCH --cpus-per-task=1
# SBATCH -p normal
# SBATCH -t 03:00:00
# SBATCH --exclusive
# SBATCH --job-name xdd_to_parquet

source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate
mpirun python3 statemod_data_extraction.py -i ./ids.txt