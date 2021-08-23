#!/bin/bash

declare -a StringArray=("xdd" "b43" "b44" "b45" "b47" "b67" "b68" "chk" "log" "tmp" "xca" "xir" "xop" "xpl" "xre" "xrp" "xss")

for dir in */; do
  for val in ${StringArray[@]}; do
    rm $dir*.$val
  done
done