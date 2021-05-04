#!/bin/bash

while getopts "I:O:" opt; do
    case ${opt} in
        I )
            in_dir=${OPTARG}
	    echo "-I = ${in_dir}"
            ;;
        O )
            out_dir=${OPTARG}
	    echo "-O = ${out_dir}"
            ;;
	* )
	    echo "[Notice] Ignoring flag  -${OPTARG}."
            ;;
    esac
done
shift $((OPTIND-1))

# ------------ Unzip All Zips  ------------
in_zips=($(find "${in_dir}" -name "*.zip"))
echo $in_zips
for ii in "${in_zips[@]}"; do
    echo "Unzipping file: ${ii}"
    unzip -o -j "${ii}" -d "${in_dir}"
done


# ------------ Get Input Files ------------
look_for=".faa"
in_files=($(find "${in_dir}" -name "*${look_for}"))
basenames=()
for ii in "${in_files[@]}"; do
    in_basenames+=($(basename ${ii} "${look_for}"))
    echo "Input file: ${ii}"
done

# ------------ Generate Fake Output Files ------------

for ii in "${in_basenames[@]}"; do
  echo "Generating output files for input file: ${ii}"
  echo "This is a fake file for testing purposes." > ${out_dir}/${ii}_fa.gff
done
