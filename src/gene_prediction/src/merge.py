#!/projects/team-1/devops/anaconda3/envs/gene_prediction/bin/python3

import argparse
import subprocess
import os
import os.path
import shutil

parser=argparse.ArgumentParser()
parser.add_argument("-i", required=True, help="full path to input folder with gff files")
parser.add_argument("-f", required=True, help="full path to input folder with fasta files")
parser.add_argument("-o", required=True, help="full path to output folder")
parser.add_argument("-a", action="store_true", help="run aragorn")
parser.add_argument("-r", action="store_true", help="run rnammer")
parser.add_argument("-p", action="store_true", help="run prodigal")
parser.add_argument("-gm", action="store_true", help="run genemark")
parser.add_argument("-gl", action="store_true", help="run glimmer")

args = parser.parse_args()

print("Making gene_prediction_output/sorted_gene_prediction/ folder")
if not os.path.exists(args.o + "/gene_prediction_output/sorted_gene_prediction/"):
	os.mkdir(args.o + "/gene_prediction_output/sorted_gene_prediction/")

#if not os.path.exists(args.o + "final_gene_prediction_output/"):
#	os.mkdir(args.o + "final_gene_prediction_output/")

#if not os.path.exists(args.o + "gene_prediction_merge_gff_output/"):
	#os.mkdir(args.o + "gene_prediction_merge_gff_output/")

#if not os.path.exists(args.o + "gene_prediction_combineall/"):
        #os.mkdir(args.o + "gene_prediction_combineall")

#if not os.path.exists(args.o + "gene_prediction_all_outputs/"):
        #os.mkdir(args.o + "gene_prediction_all_outputs/")

input_list=[]

print("making list with gff files")
for file in os.scandir(args.i):
	if file.path.endswith(".gff"):
		input_list.append(file.path)

x = os.listdir(args.i)

samples = []

for each in x:
	samples.append(each) 

def sort(sorted_file):
	print("sorting gff files")
	basename=os.path.basename(sorted_file)
	basename=basename.replace("_genemark.gff", "")
	basename=basename.replace("_prodigal.gff", "")
	basename=basename.replace("_glimmer.gff", "")
	output_name=args.o + "/gene_prediction_output/sorted_gene_prediction/"
	if args.gm==True:
		os.system("bedtools sort -chrThenSizeD -i "+args.i + basename + "_genemark.gff > "+ output_name + basename + "_genemark_sorted.gff")
	if args.p==True:
		os.system("bedtools sort -chrThenSizeD -i "+args.i + basename + "_prodigal.gff > "+ output_name + basename + "_prodigal_sorted.gff")
	if args.gl==True:
		os.system("bedtools sort -chrThenSizeD -i "+args.i + basename + "_glimmer.gff > " + output_name + basename + "_glimmer_sorted.gff")



def merge(gff_file):
	print("running merge")
	basename=os.path.basename(gff_file)
	basename=basename.replace("_glimmer_sorted.gff","")
	basename=basename.replace("_genemark_sorted.gff","")
	basename=basename.replace("_prodigal_sorted.gff","")
	input_name=args.o + "/gene_prediction_output/sorted_gene_prediction/"
	output_name=args.o

#intersect of all three
	if args.gm==True and args.p==True and args.gl==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_prodigal_sorted.gff -b "+ input_name + basename + "_genemark_sorted.gff " + input_name + basename + "_glimmer_sorted.gff > "+ output_name + basename + "_gp.gff")
	
#intersect of prodigal and genemark only
	elif args.p==True and args.gm==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_prodigal_sorted.gff -b "+ input_name + basename + "_genemark_sorted.gff > " + output_name + basename + "_gp.gff")


#intersect of glimmer and genemark only
	elif args.gl==True and args.gm==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_glimmer_sorted.gff -b "+ input_name + basename + "_genemark_sorted.gff > "+ output_name + basename + "_gp.gff")

		
#intersect of glimmer and prodigal only
	elif args.gl==True and args.p==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_prodigal_sorted.gff -b "+ input_name + basename + "_glimmer_sorted.gff > "+ output_name + basename + "_gp.gff")

#prodigal only
	elif args.p==True:
		shutil.copy(input_name + basename + "_prodigal_sorted.gff", output_name + basename + "_gp.gff")

#genemark only
	elif args.gm==True:
		shutil.copy(input_name + basename + "_genemark_sorted.gff", output_name + basename + "_gp.gff")	

#glimmer only
	elif args.gl==True:
		shutil.copy(input_name + basename + "_glimmer_sorted.gff", output_name + basename + "_gp.gff")
	print("generating fasta")
#generate fasta
	os.system("bedtools getfasta -fi " + args.f + "/" + basename + ".fasta -bed " + output_name + basename + "_gp.gff -fo "+ output_name + basename + "_gp.fna")
	print("generating faa")
#generate faa file
	os.system("transeq -sequence "+ output_name + basename + "_gp.fna -outseq "+ output_name + basename + "_gp.faa")

for i in input_list:
	sort(i)

y = os.listdir(args.o + "/gene_prediction_output/sorted_gene_prediction/")

sorted_samples = []

for each in y:
        if each not in sorted_samples:
                sorted_samples.append(each)

for k in sorted_samples:
	merge(k)
#For #generate fasta, the variable "fasta_file" is from the pipeline where it draws from genome assembly file names
