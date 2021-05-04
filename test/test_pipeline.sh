#!/bin/bash
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate genome_assembly 

#/projects/team-1/src/genome_assembly/genome_assembly_slim.sh /home/scleland7/test_full_pipeline/

conda deactivate 
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate gene_prediction
#always add forward slash for directories
#set threads to 1
#default option is to run prodigal, set up through django

#/projects/team-1/src/gene_prediction/src/gene_prediction_master.py -i /home/scleland7/more_deeparg/ -t 1 -o /home/scleland7/more_deeparg/ -p -gm -gl


conda deactivate
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate functional_annotation
python /projects/team-1/src/functional_annotation/functional_annotation_combined.py -I /home/scleland7/fun_annot/ -D /projects/team-1/tools/functional_annotation/fun_annot/ -O /home/scleland7/fun_annot/ -E /projects/team-1/tools/functional_annotation/eggnog_database_bact -p
#-u /projects/team-1/tools/functional_annotation/usearch11.0.667_i86linux32

conda deactivate 
source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh
conda activate comparative_genomics
#/projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/Comparative_master_pipeline.sh -o scleland7 -I /home/scleland7/more_deeparg/ -s CGT1808 -O /home/scleland7/more_deeparg/ -i /home/scleland7/more_deeparg/ -a  /home/scleland7/more_deeparg/ -r /projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/camplo_ref.fna -m -M -p -V -R

