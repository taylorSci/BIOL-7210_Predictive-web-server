#!/usr/bin/bash

print_help() { echo "
USAGE
	genome_assembly [OPTIONS...] <INPUT_READS_DIRECTORY>

DESCRIPTION
A script to run a pipeline which assembles sets of paired-end reads in FASTQ format into genome assemblies with multiple tools.
Preprocesses input reads, provides assembly quality metrics, and attempts to reconcile assemblies into meta-assemblies.
Sequence alignment maps are generated on assemblies to assist with QC and reconciliation.
Developed on Illumina bridge amplification dye sequencing data.

TOOLS INSTALLED/INVOKED:
	Read quality:
		Fastp
	Genome assembly:
		SPAdes

OPTIONS
	-h 										display help
	-M	<cut_mean_quality>			28		fastp: the mean quality requirement option shared by cut_front, cut_tail or cut_sliding. Range: 1~36
	-e	<average_qual>				28		fastp: if the average quality score of one read <avg_qual, then this read/pair is discarded. 0 means no requirement
	-W	<cut_window_size>			20		fastp: the window size option shared by cut_front, cut_tail or cut_sliding. Range: 1~1000
"
}

# Parse optional arguments
cut_mean_quality=28
average_qual=28
cut_window_size=20
while getopts "hM:e:W:" option
do
	case $option in
		h) 	print_help
			exit;;
		M)	cut_mean_quality=$OPTARG;;
		e)	average_qual=$OPTARG;;
		W)	cut_window_size=$OPTARG;;
		*) 	echo "UNKNOWN OPTION $OPTARG PROVIDED"
			exit;;
	esac
done

# Parse positional arguments
inputDir=$(realpath ${@:$OPTIND:1})
echo "***********inputDirs: $inputDir"

# Make temporary output directory from which to pull output files
outputDir=$inputDir/temp
echo "***********outputDir: $outputDir"
mkdir -p $outputDir

isolates=$(ls $inputDir/*.zip | xargs -I % basename % .zip)

fastpDir=$outputDir/read_QC/fastp
SPAdesDir=$outputDir/assemblies/SPAdes
SPAdesContigs=$SPAdesDir/contigs/\${PATTERN}_SPAdes.fasta
echo "***********fastpDir: $fastpDir"
echo "***********SPAdesDir: $SPAdesDir"


# Unpacking zipped sequencing read content
for i in $isolates
do
        echo "*******Unzipping isolate: $i"
	mkdir -p $outputDir/$i
	unzip $inputDir/$i.zip -d $outputDir/$i
done

# Preprocess reads
echo "Analyzing and trimming reads..."
mkdir -p $fastpDir
for i in $isolates
do
	mkdir -p $fastpDir/$i
	cd $fastpDir/$i
	read1=$(basename $(ls $outputDir/$i | head -n1) .fq.gz)
	read2=$(basename $(ls $outputDir/$i | tail -n1) .fq.gz)
        echo "********* Trimming read1: $read1"
        echo "********* Trimming read2: $read2"
	fastp -i $outputDir/$i/$read1.fq.gz -I $outputDir/$i/$read2.fq.gz -o $fastpDir/$i/${read1}_fp.fq.gz -O $fastpDir/$i/${read2}_fp.fq.gz -f 5 -t 5 -5 -3 -M $cut_mean_quality -W $cut_window_size -e $average_qual -c
done

echo "Assembling with SPAdes..."
mkdir -p $SPAdesDir/extra

for i in $isolates;
do 
	# Run SPAdes
        echo "********* Assembling isolate: $i"
	spades.py -1 $fastpDir/$i/${i}_1_fp.fq.gz -2 $fastpDir/$i/${i}_2_fp.fq.gz -o $SPAdesDir/extra/$i -t 4
	
	# Hardlink output files from temp folder into input directory
	ln $SPAdesDir/extra/$i/contigs.fasta $inputDir/$i.fasta
        echo "************Hardlink: $SPAdesDir/extra/$i/contigs.fasta --> $inputDir/$i.fasta"
	ln $fastpDir/$i/fastp.html $inputDir/$i.html
	echo "************Hardlink: $fastpDir/$i/fastp.html --> $inputDir/$i.html"
done

# Remove temp folder
# rm -r $outputDir

