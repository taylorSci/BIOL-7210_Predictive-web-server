This document describes the output files for each stage of the Campylobacter Jejuni Predictive Webserver.

##GENOME ASSEMBLY OUTPUT##
*.fasta: fasta nucleotide file(s). This ouput is the assembled genome of the uploaded isolate(s).

##GENE PREDICTION OUTPUT##
These files will contain annotation information about predicted genes found in the uploaded isolate(s) from the chosen gene prediction tools.

*.fna: annotated fasta nucleotide file(s).
*.faa: annotated fasta amino acid file(s).
*.gff: general feature format used to describe predicted genes. Contains gene locations but not nucleotide sequences.

##FUNCTIONAL ANNOTATION OUTPUT##
*.gff: Contains information about the resistance genes found in the uploaded isolate(s). CRISPR repeat information will also be available if PILER-CR option is run.

##COMPARATIVE GENOMICS OUTPUT##
*MLST Tree pdf: phylogenetic tree based on 7 gene MLST schema from stringMLST.
*SNP Tree pdf: phylogenetic tree created from ParseSNP. Reference used is the Camplobacter Jejuni type strain (ATCC 33560).
*ANI heatmap: ANIm output from pyANI. Blue represents a lower ANI score, while red is a higher ANI score.
*Virulence Factors Heatmap: output from BLAST. The heatmap square is green if the virulence factor is present for that isolate, and red if it is absent. 
*Resistance Genes Heatmap: output from DeepArg. The heatmap square is green if the virulence factor is present for that isolate, and red if it is absent.

##REFERENCE GENOMES IN COMPARATIVE GENOMICS OUTPUT##

References from the CDC antibiotic resistance database: https://wwwn.cdc.gov/ARIsolateBank/Search#results
*AR0412
*AR0413
*AR0414
*AR0415
*AR0419

C. jejuni type strain: 
*Camplo_ref
