# Team 1 Comparative Genomics

#### MEMBERS: 
Harini Adepu, Anneke Augenbroe, Davina Campbell, Swapna Kannan, Nikesh Kumar, Jintian Lyu, Marcus Valancius

This repository includes a script to run a Comparative Genomics pipeline. Comparative Genomics is a field of biological reseaarch whereby various computational tools are used to investiagte and draw conclusions from genomic data. This pipeline will utilize numerous tools which take in *de novo* assembled genomes or raw sequencing reads and perform whole genome, SNP, virulence, and AMR/Accessory DNA level analyses to provide insight into outbreak analysis for bacterial genomes.

**```Comparative_master_pipeline.sh```**
This script is to install and run a pipeline which takes assembled or raw fasta sequences and runs them through various tool to gain more insight into the genetic relatedness of the samples. The script can be run with and without tool installations. The script can also run as few as one tool and as many as all of the tools. Further information about the specific outputs are listed below. 
Further details available at our [class wiki page].

https://compgenomics2021.biosci.gatech.edu/Team_I_Comparative_Genomics#Multi-locus_Sequence_Typing_.28MLST.29
  
## Usage:
Comparative_master_pipeline.sh [OPTIONS...] < -o output name > [-t] [-i ASSEMBLED_INPUT_READS_DIRECTORY] [-I RAW_INPUT_READS_DIRECTORY] [-g GFF_FILES_DIRECTORY] [-r PARSNP_REFERENCE_FILE] [-b] [-m] [-M] [-p] [-P] [-V] [-R]

##### PREREQUISITES:
-    git
-    conda 
-    tools folder with SRST2 and VF database 

##### OPTIONS
        -t	    installs tools 
        -o      Output name for the files
        -i      PATH for input of  assembled .fasta files
        -I      PATH for input of raw reads. This is used for stringMLST
        -g	    PATH for annotated gff files. This is used for resistance
        -r      fasta file for the reference genome
        -s      sample name to root phylogenetic tree; MUST BE DIFFERENT THAN REFERENCE 
        -b      run pyANI with ANIb
        -m      run pyANI with ANIm
        -M      run stringMLST
        -p      run parSNP
        -P      run PlasmidFinder
        -V      run SRST2 and BLAST
        -R      Find resistance genes

##### TOOLS INSTALLED/INVOKED:
        SNP Level: parSNP
        Whole Genome Level:pyANI, stringMLST
        Virulence Level: VFDB,SRST2,BLAST
        Accessory DNA: PlasmidFinder

## ANIb
ANIb is run on Pyani. This is a Python3 module for calculating ANI and  other relatedness measures (alignment coverage, alignment lengths) for whole genome comparisons and creating summary figures. When running ANIb calculations you are using BLAST for robust analysis.

The command used was:
```
Comparative_master_pipeline.sh -t -i <assembled_fasta_input> -m -o <output name>
``` 
## ANIm
ANIm is run on Pyani. This is a Python3 module for calculating ANI and  other relatedness measures (alignment coverage, alignment lengths) for whole genome comparisons and creating summary figures. When running ANIm calcualtions you are using Mummer to calculate for robust analysis.

The command used was:
  
```
Comparative_master_pipeline.sh -t -i <assembled_fasta_input> -m -o <output name>
``` 
  
## stringMLST
stringMLST is a rapid k-mer based 7 gene MLST tool for our analyses. This tool can be easily installed and it has an input of raw sequene reads. This tool uses access to the PubMLST databases as a reference. 

For further visualizations you can use: https://github.com/achtman-lab/GrapeTree 

The command used was:
```
Comparative_master_pipeline.sh -t -I <raw input fasta file> -M -o <output name> -s <sample to root tree>
```
## parSNP
Evaluates core genome for the single nucleotide polymorphism analysis and requires a reference genome for the analysis. The tool takes assembled or raw genomes and outputs the core genome alignment, variant calls, and a maximum-likelihood tree. This tool requires a reference genome and takes in a fasta file as an input and outputs variant calls and SNP tree.

For further visualizations you can use: https://github.com/achtman-lab/GrapeTree 

The command used was:
  
```
Comparative_mater_pipeline.sh -t -i <assembled_fasta_input> -p -o <output name> -r <reference file> -s <sample to root tree>
``` 

## Virulence 
<ADD DESCRIPTION>
SRST2 was used to pull Campylobacter genes from the VFDB and then Blastn was then used to find the virulence genes. The files for the Virulence database is in the github folder. If you clone this repository, the tools folder has the required information.
  
The command used was:

```
Comparative_master_pipeline.sh -t -i <assembled_fasta_input> -V -o <output name>
```

## Antimicrobial Resistance Genes 
Taking an annotated GFF file for Antimicrobial Resistance genes, this portion of the script shows you if there is presence of a certain AMR resistance category in a particular isolate. 

```
Comparative_master_pipeline.sh -g <GFF PATH> -R -o <output name>
``` 
## Plasmidfinder 
This tool aims to identify and detect plasmid replicons and assign to Incompatibility groups. It takes sequence data (raw assembled) as input. The default parameters: Detection of replicons with 80%+ nucleotide identity, 60%+ coverage. Its outputs are matched sequences and location on sequence. Its advantage over query to blastn: immediate classification of plasmid to existing plasmid lineages.

```
Comparative_master_pipeline.sh -t -P -i <assembled_fasta_input> -o <output name> 
``` 
