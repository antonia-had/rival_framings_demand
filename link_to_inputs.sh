#!/bin/bash

declare -a InputsArray=("cm2015.ctl" "cm2015.rin" "cm2015.str" "cm2015B.ipy" "cm2015.rib" "cm2015.rih" "cm2015.ris" "cm2015.dds" "cm2015B.ddr" "cm2015.eva" "cm2015.eom" "cm2015B.tar" "cm2015B.res" "cm2015B.rer" "cm2015.ifa" "cm2015B.ifm" "cm2015.ifr" "cm2015.ifs" "cm2015B.opr" "cm2015.pln" "cm2015.dly")

declare -a StreamflowArray=("xbm" "iwr" "ddm" "rsp")

for dir in scenarios/; do
  for val in ${InputsArray[@]}; do
    ln -s ../cm2015_StateMod/StateMod/$val scenarios/$dir
  done
  for val in ${StreamflowArray}; do
    ln -s ../LHsamples_wider_100_AnnQonly/cm2015_$dir.$val scenarios/$dir
  done
  ln -s ln -s /home/ah986/statemod scenarios/$dir
done