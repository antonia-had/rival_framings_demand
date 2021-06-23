#!/bin/bash
#SBATCH --partition=compute
#SBATCH --ntasks=20
#SBATCH --time=1:45:00
#SBATCH --job-name="realization_flows"
#SBATCH --array=1-5

module load parallel
module load python
module load scipy/3.6
export MODULEPATH=/share/apps/compute/modulefiles/applications:$MODULEPATH
# This specifies the options used to run srun. The "-N1 -n1" options are
# used to allocates a single core to each task.
srun="srun --exclusive -N1 -n1"
# This specifies the options used to run GNU parallel:
#
#   --delay of 0.2 prevents overloading the controlling node.
#
#   -j is the number of tasks run simultaneously.
#
#   The combination of --joblog and --resume create a task log that
#   can be used to monitor progress.
#
parallel="parallel --delay 0.2 -j $SLURM_NTASKS --joblog runtask.log --resume"

$parallel "$srun python3 realization_flows.py" ::: {1..2} ::: {1..10}
