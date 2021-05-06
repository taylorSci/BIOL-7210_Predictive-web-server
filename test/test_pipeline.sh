#!/bin/bash
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate genome_assembly 

/projects/team-1/src/genome_assembly/genome_assembly_slim.sh /projects/team-1/test/data/input_tests/CGT1197/

conda deactivate 
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate gene_prediction
#always add forward slash for directories
#set threads to 1
#default option is to run prodigal, set up through django

/projects/team-1/src/gene_prediction/src/gene_prediction_master.py -i /projects/team-1/test/data/input_tests/CGT1197/ -t 1 -o /projects/team-1/test/data/input_tests/CGT1197/ -p -gm -gl


conda deactivate
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate functional_annotation

python /projects/team-1/src/functional_annotation/functional_annotation_combined.py -I /projects/team-1/test/data/input_tests/CGT1197/ -D /projects/team-1/tools/functional_annotation/deeparg_database/ -O /projects/team-1/test/data/input_tests/CGT1197/ -p -u /projects/team-1/tools/functional_annotation/usearch11.0.667_i86linux32

conda deactivate 
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate comparative_genomics
/projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/Comparative_master_pipeline.sh -o 1197_test -I /projects/team-1/test/data/input_tests/CGT1197/ -s  CGT1808 -O /projects/team-1/test/data/input_tests/CGT1197/ -i /projects/team-1/test/data/input_tests/CGT1197/ -a /projects/team-1/test/data/input_tests/CGT1197/ -r /projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/camplo_ref.fna -m -M -p -V -R

