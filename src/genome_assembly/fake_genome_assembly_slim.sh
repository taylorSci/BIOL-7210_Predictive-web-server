#!/bin/bash

for last; do true; done

in_dir="${last}"
out_dir="${last}"
echo "Output and Input Directory: $in_dir"

# ------------ Unzip All Zips  ------------
in_zips=($(find "${in_dir}" -name "*.zip"))
echo $in_zips
for ii in "${in_zips[@]}"; do
    echo "Unzipping file: ${ii}"
    unzip -o -j "${ii}" -d "${in_dir}"
done


# ------------ Get Input Files ------------
look_for=".fq.gz"
in_files=($(find "${in_dir}" -name "*${look_for}"))
basenames=()
for ii in "${in_files[@]}"; do
    in_basenames+=($(basename ${ii} "${look_for}"))
    echo "Input file: ${ii}"
done

# ------------ Generate Fake Output Files ------------

for ii in "${in_zips[@]}"; do
  echo "Generating output files for input file: ${ii}"
  basename=$(basename $ii .zip)
  echo "This is a fake file for testing purposes." > ${out_dir}/${basename}.fasta
  echo "This is a fake file for testing purposes." > ${out_dir}/${basename}.html
done

