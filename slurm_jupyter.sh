#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=04:00:00
#SBATCH --job-name=jupyter_launch
#SBATCH --output=jupyter-%j.log
#SBATCH --error=jupyter-%j.err

source /home/fs02/pmr82_0001/ah986/rival_framings/bin/activate

# set a random port for the notebook, in case multiple notebooks are
# on the same compute node.
NOTEBOOKPORT=`shuf -i 18000-18500 -n 1`

# set a random port for tunneling, in case multiple connections are happening
# on the same login node.
TUNNELPORT=`shuf -i 18501-19000 -n 1`

# Set up a reverse SSH tunnel from the compute node back to the submitting host (login01 or login02)
# This is the machine we will connect to with SSH forward tunneling from our client.
ssh -R$TUNNELPORT:localhost:$NOTEBOOKPORT $SLURM_SUBMIT_HOST -N -f

echo "FWDSSH='ssh -L8888:localhost:$TUNNELPORT $(whoami)@$SLURM_SUBMIT_HOST -N'"

# Start the notebook
srun -n1 jupyter notebook --no-browser --no-mathjax --port=$NOTEBOOKPORT

wait
