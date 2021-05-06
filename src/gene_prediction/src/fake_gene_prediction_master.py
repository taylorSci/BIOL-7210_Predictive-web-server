#!/bin/bash

while getopts "i:o:" opt; do
    case ${opt} in
        i )
            in_dir=${OPTARG}
	    echo "-i = ${in_dir}"
            ;;
        o )
            out_dir=${OPTARG}
	    echo "-o = ${out_dir}"
            ;;
	* )
	    echo "[Notice] Ignoring flag  -${OPTARG}."
            ;;
    esac
done
shift $((OPTIND-1))

# ------------ Unzip All Zips  ------------
in_zips=($(find "${in_dir}" -name "*.zip"))
for ii in "${in_zips[@]}"; do
    unzip -j "${ii}" -d "${in_dir}"
done

# ------------ Get Input Files ------------
in_files=($(find "${in_dir}" -name "*.fasta"))
basenames=()
for ii in "${in_files[@]}"; do
    in_basenames+=($(basename ${ii} ".fasta"))
    echo "Input file: ${ii}"
done

# ------------ Generate Fake Output Files ------------
for ii in "${in_basenames[@]}"; do
  echo "Generating output files for input file: ${ii}"
  echo "This is a fake file for testing purposes." > ${out_dir}/${ii}_gp.faa
  echo "This is a fake file for testing purposes." > ${out_dir}/${ii}_gp.fna
  echo "This is a fake file for testing purposes." > ${out_dir}/${ii}_gp.gff
done

