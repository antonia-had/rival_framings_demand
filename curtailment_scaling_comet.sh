#!/bin/bash
#SBATCH --partition=compute
#SBATCH --nodes=1             # specify number of nodes
#SBATCH --ntasks-per-node=1  # specify number of core per node
#SBATCH --export=ALL
#SBATCH -t 1:45:00            # set max wallclock time
#SBATCH --job-name="statemod" # name your job
#SBATCH --output="curtailment_runs.out"
#SBATCH --mail-user=ah986@cornell.edu
#SBATCH --mail-type=ALL

module load python
module load scipy/3.6
export MODULEPATH=/share/apps/compute/modulefiles/applications:$MODULEPATH
module load mpi4py
export MV2_ENABLE_AFFINITY=0
source /home/ah986/rival_framings_demand/bin/activate
ibrun python3 curtailment_scaling.py