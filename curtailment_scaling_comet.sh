#!/bin/bash
#SBATCH --partition=compute
#SBATCH --ntasks=24
#SBATCH --time=1:30:00
#SBATCH --job-name="curtailment_scaling_$1"
#SBATCH --output="./outputs/curtailment_scaling_$1.out"
#SBATCH --error="./errors/curtailment_scaling_$1.err"
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load parallel
module load miniconda
source activate /home/ah986/miniconda3/envs/adaptive_demands
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
parallel="parallel --delay 0.2 -j $SLURM_NTASKS --joblog curtailment_scaling.log"
echo "Submitting job # $1 for samples $2 to $3"
$parallel "$srun python3 curtailment_scaling.py" ::: {1..2} ::: {1..2} ::: {$2..$3}
