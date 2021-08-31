#!/bin/bash

for i in $(seq 1 100); do
  for j in $(seq 1 10); do
    for k in $(seq 1 500); do
      file="xdd_parquet/S${i}_${j}/S${i}_${j}_${k}.parquet"
      if [ ! -f $file ]; then
        echo -e "$i $j $k" >> missing_runs.txt
      fi
    done
  done
done
