#!/bin/bash

# This script submits a Slurm job to get resources and
# start a Jupyter notebook on those resources.

jobid=$(sbatch --parsable slurm_jupyter.sh)
workdir=$(squeue --format=%Z --noheader -j $jobid)
logfile=$workdir/jupyter-$jobid.log
errfile=$workdir/jupyter-$jobid.err

echo -n "Waiting for notebook to start  "

# wait for the logfile to appear and be not-empty
sp="/-\|"
while [ ! -s $logfile ]
do
    printf "\b${sp:i++%${#sp}:1}"
    sleep 1;
done

. $logfile

token=""
sleep 5
token=$(tail -1 $errfile | awk 'BEGIN { FS="="} ; { print $2 }')

echo ""
echo "1) Tunnel to the cluster from your laptop: run this command on your laptop:"
echo "    $FWDSSH"

if [ -z $token ]
then
  echo "2) If you've set a notebook password, point your browser to:"
  echo "    http://localhost:8888"
  echo "(waited 5 seconds for token to appear. If you expected a token,"
  echo " you can find it in $errfile)"
else
  echo "2) and point your browser to:"
  echo "    http://localhost:8888?token=$token"
fi

echo "If port 8888 is already in use on your laptop, you can change to another number"
echo "in both the ssh tunnel command and the 'localhost:nnnn' address"
echo "Close the notebook with:"
echo "    scancel $jobid"
