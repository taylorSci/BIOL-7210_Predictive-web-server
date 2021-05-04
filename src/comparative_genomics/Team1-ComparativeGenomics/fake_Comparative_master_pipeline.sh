#!/bin/bash

while getopts "i:O:o:mMpVR" opt; do
    case ${opt} in
        i )
            in_dir=${OPTARG}
	    echo "-i = ${in_dir}"
            ;;
        O )
            out_dir=${OPTARG}
	    echo "-O = ${out_dir}"
            ;;
	o )
            in_basenames=${OPTARG}
	    echo "-o = ${in_basenames}"
            ;;
	m) m=true;;
	M) M=true;;
	p) p=true;;
	V) V=true;;
 	R) R=true;;
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

# ------------ Generate Fake Output Files ------------

if [[ $m == true ]]; then
    echo m
    convert -size 32x32 xc:black ${out_dir}/ANIm_percentage_identity.png
fi

if [[ $M == true ]]; then
    echo M
    convert -size 32x32 xc:yellow ${out_dir}/MLSTtree_${in_basenames}.pdf
fi

if [[ $p == true ]]; then
    echo p
    convert -size 32x32 xc:blue ${out_dir}/SNP_${in_basenames}.pdf
fi

if [[ $V == true ]]; then
    echo V
    convert -size 32x32 xc:pink ${out_dir}/res_table_${in_basenames}.png
fi

if [[ $R == true ]]; then
    echo R
    convert -size 32x32 xc:green ${out_dir}/VF_table_${in_basenames}.png	
fi
