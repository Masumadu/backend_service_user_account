#!/bin/bash

# directories to check
check_dirs=("api/api_v1/endpoints"  "controllers")

for dir in "${check_dirs[@]}"; do
  # get absolute path
  dir_abs_path="$(pwd)/app/$dir"
  # loop through files in directory
 for file in "$dir_abs_path"/*
  do
    if [[ "$file" == *.py ]]
    then
      if ! poetry run coverage report --fail-under=95 "$file"
      then
        exit 1
      fi
    fi
  done
done
