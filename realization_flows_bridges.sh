#!/bin/bash
#SBATCH --partition=RM
#SBATCH --ntasks=100
#SBATCH --time=00:30:00
#SBATCH --job-name="realization_flows"
#SBATCH --output="./outputs/realization_flows.out"
#SBATCH --error="./errors/realization_flows.err"
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load parallel
module load anaconda3
eval "$(conda shell.bash hook)"
conda activate /ocean/projects/ees200007p/ah986/.conda/envs/adaptive_demands
# This specifies the options used to run srun. The "-N1 -n1" options are
# used to allocates a single core to each task.
srun="srun --export=all --exclusive -N1 -n1"
# This specifies the options used to run GNU parallel:
#
#   --delay of 0.2 prevents overloading the controlling node.
#
#   -j is the number of tasks run simultaneously.
#
#   The combination of --joblog and --resume create a task log that
#   can be used to monitor progress.
#
parallel="parallel --delay 0.2 -j $SLURM_NTASKS --joblog runtask.log"

$parallel "$srun python3 realization_flows.py" ::: {1..100} ::: {1..10}
