# Team 1 Gene Prediction

#### MEMBERS:
Davina Campbell, Sara Cleland, James Matthew Hamilton, Hyojung Kim, Sai Kollapaneni, Anantharaman Shantaraman​

#### PIPELINE OVERVIEW:

Gene prediction is the process of identification of regions of genomic DNA that encode genes. This pipeline uses several tools to predict protein-coding genes, RNA genes, and other functional elements of the genome such as regulatory regions.

##### TOOLS INSTALLED/INVOKED: 
Prodigal\
ARAGORN\
Glimmer\
Diamond\
bedtools\
EMBOSS\
GeneMark-S2\
RNAmmer\
HMMer 2.3\
XML/Simple.pm perl package

## Quick Start 

Inputs:
```
-i: Path to input file directory (required)
-t: Number of threads. Default is one.
-o: Path to output directory (required)
```
Example Usage:

```
./gene_prediction_master.py -i /home/team1/genome_assembly/output/assembly-reconciliation/ -t 5 -o /home/
```
This command will run the `gene_prediction_pipeline.py`, which outputs results for all 5 gene prediction tools. It will then run `merge.py`, which merges all the outputs together.

## Coding Ab-Initio Tools

### Glimmer
```
./Glimmer.csh [input fasta file] [output location & prefix]
```
### Genemark
```
gms2.pl --seq [INPUT FASTA FILE] --genome-type auto --format gff --output [OUTPUT FILE] 
```
### Prodigal
```
prodigal -i [input fasta file] -o [output file] -f [output format]
```
## Coding Homology Tools

### Diamond 
- makedb command creats Diamond formatted database
- blastp command align protein query seqeunces against a protein database
- the --max-target-seqs 0 reports all alignments that were found
- the --more-sensitive sets more sensitive mode which is a lot more sensitive that the default and generally recommended for aligning
longer sequences
```
diamond makedb --in [input file: faa] -d [output file]
diamond blastx -q [input file: fna] -d [DB file] -o [output file] --max-target-seqs 0 --more-sensitive
```

## Non-Coding Ab-Initio Tools

### RNAmmer

### ARAGORN
```
aragorn -w [input fasta file] -o [output file name]
```
## Output
The final output can be found in the `gene_prediction_all_outputs` folder. Each genome will have a .gff, .fna, and .faa file. 

### Coding Output
```
bedtools sort -chrThenSizeD -i [input gff file] > [output gff file]
```
```
bedtools intersect -f [minimum overlap] -r -a [tool A gff file] -b [tool B gff file] [tool C gff file] > [output gff file] 

-f: minimum overlap as a fraction of A 
-r: requirement that minimum fraction be satisfied for A or B 
```
```
bedtools getfasta -f [input fasta file] -bed [input gff file] -fo [out fna file]
transeq -sequence [input fna file] -outseq [output faa file]
```
### Non-Coding Output
The ARAGORN and RNAmmer output are concatenated together to create the non-coding output.
```
	tail -n +7 output_rnammer.gff | head -n -1 >> output_aragorn.gff
 ```
 ### Combining all Outputs
 The intersected coding output is then concatenated with the non-coding output and converted to an fna file. The non-coding output is not converted to an faa file since rRNAs and tRNAS do not become proteins. 
 ```
 bedtools getfasta -f [input fasta file] -bed [input gff file] -fo [out fna file]
 ```



