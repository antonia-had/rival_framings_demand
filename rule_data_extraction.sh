#!/bin/bash
#SBATCH --nodes=15
#SBATCH --ntasks-per-node=12
#SBATCH -t 5:00:00
#SBATCH --export=ALL
#SBATCH --exclusive
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate
mpirun python3 rule_data_extraction.py
