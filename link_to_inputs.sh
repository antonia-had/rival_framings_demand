#!/bin/bash

declare -a InputsArray=("cm2015.ctl" "cm2015.rin" "cm2015.str" "cm2015B.ipy" "cm2015.rib" "cm2015.rih" "cm2015.ris" "cm2015.dds" "cm2015B.ddr" "cm2015.eva" "cm2015.eom" "cm2015B.tar" "cm2015B.res" "cm2015B.rer" "cm2015.ifa" "cm2015B.ifm" "cm2015.ifr" "cm2015.ifs" "cm2015B.opr" "cm2015.pln" "cm2015.dly")

for dir in scenarios/*; do
  subdir=$(echo $dir | cut -d'/' -f 2)
  for val in ${InputsArray[@]}; do
    rm $dir/$val
    ln -s /expanse/lustre/scratch/ah986/temp_project/cm2015_StateMod/StateMod/$val $dir
  done
  ln -s /expanse/lustre/scratch/ah986/temp_project/LHsamples_wider_100_AnnQonly/cm2015x_$subdir.xbm $dir
  ln -s /home/ah986/statemod $dir
  mkdir xdd_parquet/$subdir
done