#!/bin/bash
#Usage that the user is going to see
print_help() { echo "
USAGE
        Comparative_master_pipeline [OPTIONS...] < -o output name > [-t] [-i ASSEMBLED_INPUT_READS_DIRECTORY] [-I RAW_INPUT_READS_DIRECTORY] [-g GFF_FILES_DIRECTORY] [-r PARSNP_REFERENCE_FILE] [-b] [-m] [-M] [-p] [-P] [-V] [-R]


DESCRIPTION
This is a script to install and run a pipeline for Comparative Genomics Analysis.
There are multiple tools that you can choose from and run.
The script takes in FASTA files for ANI, SNP analysis, Virulence and PlasmidFinder. It takes in raw reads for MLST and it takes in gff annotated files to find resistance genes.

PREREQUISTITES:
        git
        conda
        tools folder with SRST2 and VF database

TOOLS INSTALLED/INVOKED:
        SNP Level: parSNP
        Whole Genome Level:pyANI, stringMLST
        Virulence Level: VFDB,SRST2,BLAST
        Accessory DNA: PlasmidFinder
OPTIONS
        -t	installs tools 
        -o      Output name for the files
	-O	Output path for the files
        -i      PATH for input of  assembled .fasta files
        -I      PATH for input of raw reads. This is used for stringMLST
        -g	PATH for annotated gff files. This is used for resistance
        -r      fasta file for the reference genome
        -b      run pyANI with ANIb
        -m      run pyANI with ANIm
        -M      run stringMLST
        -p      run parSNP NOTE: when running parSNP, pass the -r command and select a sample for your reference, then pass the -s command and select a DIFFERENT sample for rooting the tree
        -P      run PlasmidFinder
        -V      run SRST2 and BLAST
        -R      Find resistance genes
"
}

#our GETOPTS BLOCK
assembled_input=$false
raw_input=$false
ref_genome=$false
gff_files=false
ANIb=false
ANIm=false
stringMLST=false
PlasmidFinder=false
parSNP=false
virulence=false
resistance=false
tools=false
sample=$false




while getopts "ha:i:I:r:g:o:O:s:bmMpPVRt" option
do
	case $option in
		h) print_help
			exit;;
		a)	all_input=$OPTARG;;
		i) 	assembled_input=$OPTARG;;
		I) 	raw_input=$OPTARG;;
		r) 	ref_genome=$OPTARG;;
		g) 	gff_files=$OPTARG;;
		o) 	output=$OPTARG;;
		O)	output_path=$OPTARG;;
		s) 	sample=$OPTARG;;
		b) 	ANIb=true;;
		m) 	ANIm=true;;
		M) 	stringMLST=true;;
		p) 	parSNP=true;;
		P) 	PlasmidFinder=true;;
		V) 	virulence=true;;
		R) 	resistance=true;;
		t) 	tools=true;;
		*) 	echo "UNKNOWN OPTION PROVIDED"
			exit;; #isnt echoing the option provided
	esac
done


## UNZIPPING INPUT FILE ###
isolates=$(ls ${all_input}/*.zip | xargs -I % basename % .zip)
for i in $isolates
do
	unzip $all_input/$i.zip -d $output_path
        mv $all_input/$i/* $output_path/
	rmdir $all_input/$i/
done



# make general CompGen directory with tools and outputs 
#mkdir -p CompGen/tools CompGen/output


mkdir ${all_input}/assembled_reads
cp /projects/team-1/src/comparative_genomics/assembly_subset/*.fasta ${all_input}/assembled_reads/
cp ${all_input}/*.fasta ${all_input}/assembled_reads/


# running aniB
if $ANIb; then
	
	#check if input files exist
	if [ $ANIb -a -z $assembled_input ]
	then 
		echo "Assemblies do not exist. Please call the -i flag and provide a path to the input directory of assembled reads"
		exit
	fi

	#make tools and output directory for ANIm
	mkdir -p CompGen/tools/ANIb CompGen/tools/ANIb/extra CompGen/output/ANIb
	
	conda create --name pyani_env python=3.8 -y
	eval "$(conda shell.bash hook)"
	source /projects/team-1/devops/anaconda3/bin/activate pyani_env
	conda activate pyani_env
		
	#download tools
	echo "Installing pyani..."
	#conda install -y biopython
	#conda install -y -c bioconda pyani
	#conda install -y -c bioconda blast-legacy
	#conda install -y -c bioconda/label/cf201901 blast-legacy
	#conda install -y -c biocore blast-legacy
	
	
	#run the ANIm command
	echo "Calculating average nucleotide identity using ANIm..."
	average_nucleotide_identity.py -o CompGen/output/ANIb/$output -i $assembled_input -m ANIb -g -f -v
	
	#deactivate pyani_env
	conda deactivate
	#conda env remove -n pyani_env

fi

#running aniM
if $ANIm; then
	echo "starting ANIm processes"
	#check if input files exist
	if [ $ANIm -a -z $assembled_input ];
	then
		echo "Assemblies do not exist. Please call the -i flag and provide a path to the input directory of assembled reads"
		exit
	fi

	#make tools and output directory for ANIm
	#mkdir -p CompGen/tools/ANIm CompGen/tools/ANIm/extra $output_path/output/ANIm
	mkdir -p $output_path/ANIm

	#conda create --name pyani_env python=3.8 -y
	eval "$(conda shell.bash hook)"
	source ./anaconda3/bin/activate pyani_env
	conda activate pyani_env

	#download tools
	#echo "Installing pyani..."
	#conda install -y biopython
	#conda install -y -c bioconda pyani
	#conda install -y -c bioconda blast-legacy
	#conda install -y -c bioconda mummer blast legacy-blast
	#conda install -y -c bioconda/label/cf201901 blast-legacy
	#conda install -y -c biocore blast-legacy 
	
	#mkdir ${assembled_input}/ANI_subset
	#cp /projects/team-1/src/comparative_genomics/assembly_subset/* ${assembled_input}/ANI_subset/
	#cp ${assembled_input}/*.fasta ${assembled_input}/ANI_subset/
	
	#run the ANIm command
	#echo "Calculating average nucleotide identity using ANIm..."
	average_nucleotide_identity.py -o $output_path/ANIm/$output -i ${assembled_input}/assembled_reads -m ANIm -g -f -v --maxmatch
	cp ${output_path}/ANIm/${output}/ANIm_percentage_identity.png ${output_path}/ANIm_percentage_identity.png
	
	rm -r ${output_path}/ANIm/

	conda deactivate
	conda activate comparative_genomics
	#conda env remove -n pyani_env

fi

#running MLST
if $stringMLST; then

	# check if input files exist
	#if [ $stringMLST -a -z $raw_input ];
	#then 
	#	echo "Raw reads input for provided. Please call the -I flag and provide path to a directory of raw reads."
	#	exit
	#fi
	
	mkdir -p ${all_input}/raw_reads/
	cp ${all_input}/*.fq.gz ${all_input}/raw_reads/

	# check if Sample name provided alongside stringMLST flag
	if [ $stringMLST -a -z $sample ]; then
		echo "No sample name provided. Please call the -s flag and enter a sample name"
		exit
	fi

	#mkdir -p /projects/team-1/src/comparative_genomics/CompGen/tools/stringMLST /projects/team-1/src/comparative_genomics/CompGen/tools/stringMLST/extra CompGen/output/stringMLST

	# Install stringMLST
	if $tools; then
		echo "Installing stringMLST and its dependencies"
		conda install -c bioconda stringmlst -y

		# Install GrapeTree
		echo "Installing GrapeTree and its dependencies"
		pip install grapetree 
		conda install pandas -y
		conda install requests -y

		# Install Toytree
		echo "Installing Toytree and its dependencies"
		conda install toytree -c conda-forge -y
	fi
	
	# run stringMLST
	echo "downloading database for $species from pubMLST..."
	stringMLST.py --getMLST -P /projects/team-1/src/comparative_genomics/CompGen/tools/stringMLST/datasets/ --species "Campylobacter jejuni"
	
	echo "configuring database for $species..."
	stringMLST.py --buildDB --config /projects/team-1/src/comparative_genomics/CompGen/tools/stringMLST/datasets/Campylobacter_jejuni_config.txt -k 35 -P CJ
	
	echo "running sequence typing for paired end reads..."
	stringMLST.py --predict -d ${all_input}/raw_reads/ -p --prefix CJ -k 35 > ${output_path}/7gMLST_profile_temp.txt
	
	cat ${output_path}/7gMLST_profile_temp.txt /projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/7gMLST_sub.tsv > ${output_path}/7gMLST_${output}.tsv

	#awk 'FNR == 1; FNR > 1 && (!/Sample/)' $PWD/CompGen/output/stringMLST/7gMLST_profile_temp.txt >> $PWD/CompGen/output/stringMLST/7gMLST_${output}.tsv

	#below are the original stringMLST.py --predict commands. The ones above are to create a growing profile of samples so that old ones do not have to be rerun
	# echo "running sequence typing for paired end reads..."
	# stringMLST.py --predict -d $raw_input -p --prefix CJ -k 35 -o $PWD/CompGen/output/stringMLST/7gMLST_${output}.tsv
		
	#mv $PWD/CJ* $PWD/CompGen/tools/stringMLST/extra/
	
	echo "Done with stringMLST!"

	# run GrapeTree to generate newick file for cluster visualization
	echo "generating Newick file from allele profile"
	grapetree -p ${output_path}/7gMLST_${output}.tsv -m "MSTreeV2" > ${output_path}/7gMLST_${output}.newick
	
	echo "Newick file generated"
	echo "Generating tree PDF"

python3 - << EOF
import toytree
import toyplot
import toyplot.pdf
import numpy as np
import subprocess as sp

with open('${output_path}/7gMLST_${output}.newick', 'r') as fh:
	newick = fh.read()
print(newick)
tre = toytree.tree(newick)

#rtre = tre.root(wildcard="CGT1985")
#rtre.draw(tip_labels_align=True);

canvas, axes, mark = tre.draw(height = 450, node_labels = None, node_sizes = 5, node_colors = "red", layout = 'd', scalebar = True)

toyplot.pdf.render(canvas, "${output_path}/MLSTtree_${output}.pdf")
EOF

	echo "MLST profile tree generated"
#rm ${output_path}/7gMLST_${output}.tsv 
rm ${output_path}/7gMLST_${output}.newick ${output_path}/7gMLST_profile_temp.txt

fi

#running parsnp
if $parSNP; then

	#check if reference exists
	if [ $parSNP -a -z $ref_genome ];
	then 
		echo "Reference genome not provided. Please call the -r flag and specify an assembled genome to serve as reference."
		exit
	fi

	if [ $parSNP -a -z $sample ]; then
		echo "No sample name provided. Please call the -s flag and enter a sample name"
		exit
	fi

	if [ $sample -eq $ref_genome ]; then
		echo "For the -s flag, please provide a sample that is different from the reference."
		exit
	fi
	# check if input is correct 
	if [ $parSNP -a -z $assembled_input ]
	then 
		echo "Assembled genomes not provided. Please call the -i flag and specify the file path to assembled genomes directory"
		exit
	fi


	#make tools and output directory for parsnp
	#mkdir -p CompGen/tools/parsnp CompGen/tools/parsnp/extra CompGen/output/parsnp

	#download tools
	if $tools; then
		echo "Installing parSNP..."
		conda install -y -c bioconda parsnp

	# Install Toytree
		echo "Installing Toytree..."
		conda install toytree -c conda-forge -y
	fi 
	#run parsnp
	parsnp -r $ref_genome -d ${all_input}/assembled_reads/ -o ${output_path}/parsnp/

	# generate tree with Toytree
	python3 - << EOF
import toytree
import toyplot
import toyplot.pdf
import numpy as np
import subprocess as sp

with open('${output_path}/parsnp/parsnp.tree', 'r') as fh:
	newick = fh.read()
tre = toytree.tree(newick)

#rtre = tre.root(wildcard="${sample}")
#rtre.draw(tip_labels_align=True);

canvas, axes, mark = tre.draw(height = 450, node_labels = None, node_sizes = 5, node_colors = "red", layout = 'd', scalebar = True)

toyplot.pdf.render(canvas, "${output_path}/SNP_${output}.pdf")
EOF

	echo "SNP tree generated"
rm -r ${output_path}/parsnp/
fi

# running virulence
if $virulence; then
	
	# check if input is correct
	if  [$virulence -a -z $assembled_input ]
	then
		echo "Assemblies do not exist. Please call the -i flag and provide a path to the input directory of assembled reads"
		exit
	fi

	#make tools and output directory for virulence
	mkdir -p ${output_path}/virulence
	#/projects/team-1/src/comparative_genomics/CompGen/tools/virulence

	# make the blast database
	# makeblastdb -in projects/team-1/src/comparative_genomics/Campylobacter_VF_clustered.fasta -dbtype 'nucl' -out projects/team-1/src/comparative_genomics/Campylobacter_database

	# run blast on all the files and put results in output folder
	for file in $(ls ${all_input}/assembled_reads/*.fasta); do
		basename=${file##*/}
		#echo $basename
		blastn -db /projects/team-1/src/comparative_genomics/Campylobacter_database -query $file -perc_identity .98 -out ${output_path}/virulence/${basename} -outfmt "6 stitle"
	done


	# get all the gene names
	rm ${output_path}/virulence/VF_all_$output.txt
	for file in $(ls ${output_path}/virulence/*fasta); do
		awk '{print $3}' $file >> ${output_path}/virulence/VF_all_$output.txt
	done

	# get unique genes and add them as columns in a new file
	rm ${output_path}/VF_unique_$output.txt
	sort ${output_path}/virulence/VF_all_$output.txt | uniq >> ${output_path}/virulence/VF_unique_$output.txt
	long_line=""
	for line in $(cat ${output_path}/virulence/VF_unique_$output.txt); do
        	long_line+="	$line"
	done

	echo "$long_line" > ${output_path}/VF_table_$output.txt
	
	# check if gene is in each file and add info to VF_table.txt
	for file in $(ls ${output_path}/virulence/*fasta); do
        	
		data="$file	"
        	for line in $(cat ${output_path}/virulence/VF_unique_${output}.txt); do
                	if grep -q $line $file; then
                        	data+="X	"
               		else
                        	data+="	"
                	fi
        	done
        	echo "$data" >> ${output_path}/VF_table_$output.txt
	done
python /projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/virulencefactorplot.py -i ${output_path}/VF_table_$output.txt -o ${output_path}/VF_table_$output
rm -r ${output_path}/virulence/
rm ${output_path}/VF_unique_$output.txt
fi


#running resistance
if $resistance; then
	
	#make the output directory 
	mkdir -p ${output_path}/output/Deeparg
	cp ${all_input}/*_fa.gff ${output_path}/output/Deeparg/
	cp /projects/team-1/src/comparative_genomics/subset_gff/*.gff ${output_path}/output/Deeparg/
	rm ${output_path}/output/Deeparg/res_temp_$output.txt
	rm ${output_path}/output/Deeparg/res_all_$output.txt
	rm ${output_path}/output/Deeparg/res_unique_$output.txt
	rm ${output_path}/res_table_$output.txt
	# get all the gene names
	if [ $(find ${all_input} -name *_fa.gff) ]; then
		echo "file found"
	else
		echo "No DeepARG faa file provided. Please run functional annotation first"
	fi
	for file in $(ls ${all_input}/output/Deeparg/*.gff); do
		echo $file
		grep DeepARG $file  | awk '{print $9}' | sed 's/|/	/g' >> ${output_path}/output/Deeparg/res_temp_$output.txt
	done

	while IFS=$'\t' read -r -a myArray
	do
 		echo "${myArray[2]}" >> ${output_path}/output/Deeparg/res_all_$output.txt
	done < ${output_path}/output/Deeparg/res_temp_$output.txt 


	# get unique genes and add them as columns in a new file
	sort ${output_path}/output/Deeparg/res_all_$output.txt | uniq >> ${output_path}/output/Deeparg/res_unique_$output.txt
	long_line=""
	for line in $(cat ${output_path}/output/Deeparg/res_unique_$output.txt); do
		long_line+="	$line"
	done

	echo "$long_line" > ${output_path}/res_table_$output.txt

	# check if gene is in each file and add info to res_table.txt
	for file in $(ls $all_input/output/Deeparg/*.gff); do
		data="$file	"
		for line in $(cat ${output_path}/output/Deeparg/res_unique_$output.txt); do
			if grep -q ${line} ${file}; then
				data+="X	"
			else
				data+="	"
			fi
		done
		echo "$data" >> ${output_path}/res_table_$output.txt
	done

python /projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/virulencefactorplot.py -i ${output_path}/res_table_$output.txt -o ${output_path}/res_table_$output
rm -r ${output_path}/output/Deeparg/
rm ${output_path}/res_table_$output.txt
fi 

#running PlasmidFinder
if $PlasmidFinder; then
	
	# check if input is correct 
	if [ $PlasmidFinder -a -z $assembled_input ]
	then
		echo "Assemblies do not exist. Please call the -i flag and provide a path to the input directory of assembled reads"
		exit
	fi
	
	#making the directories
	mkdir -p CompGen/tools CompGen/tools/PlasmidFinder/extra CompGen/output/PlasmidFinder
	#cd CompGen/tools/PlasmidFinder
	
	#installing PlasmidFinder
	if $tools; then
		echo "Installing Plasmidfinder"
		conda install -c bioconda plasmidfinder -y
		download-db.sh
	fi
	
	echo "Running plasmidfinder"  
    	for file in $(ls $assembled_input); do
    		echo "$file"
    		v=$(echo $file | cut -d "." -f 1)
    		v1="${output}${v}"
    		plasmidfinder.py -i $assembled_input/$file > CompGen/output/PlasmidFinder/$v1 
    	done

	mv data.json CompGen/output/PlasmidFinder/${output}_data.json
	mv tmp $PWD/CompGen/tools/PlasmidFinder
fi
rm -r ${all_input}/assembled_reads/
rm -r ${all_input}/deeparg/
rm -r ${all_input}/output/
