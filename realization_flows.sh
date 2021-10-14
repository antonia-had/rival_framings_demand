#!/bin/bash
#SBATCH --partition=shared
#SBATCH --account=TG-EAR090013
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=100
#SBATCH --time=00:30:00
#SBATCH --job-name="realization_flows"
#SBATCH --output="./outputs/realization_flows.out"
#SBATCH --error="./errors/realization_flows.err"
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load anaconda3

module load cpu/0.15.4
module load parallel
source activate /home/ah986/.conda/envs/adaptive_demands
# This specifies the options used to run srun. The "-N1 -n1" options are
# used to allocates a single core to each task.
srun="srun --export=all"
# This specifies the options used to run GNU parallel:
#
#   --delay of 0.2 prevents overloading the controlling node.
#
#   -j is the number of tasks run simultaneously.
#
#   The combination of --joblog and --resume create a task log that
#   can be used to monitor progress.
#
parallel="parallel --delay 0.2 -j $SLURM_NTASKS --joblog realization_flows.log"

$srun $parallel "python3 realization_flows.py" ::: {1..100} ::: {1..10}