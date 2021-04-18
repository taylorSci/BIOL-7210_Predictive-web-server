#!/projects/team-1/devops/anaconda3/envs/webserver/bin/python3


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

if not os.path.exists(args.o + "sorted_gene_prediction/"):
	os.mkdir(args.o + "sorted_gene_prediction/")

if not os.path.exists(args.o + "final_gene_prediction_output/"):
	os.mkdir(args.o + "final_gene_prediction_output/")

#if not os.path.exists(args.o + "gene_prediction_merge_gff_output/"):
	#os.mkdir(args.o + "gene_prediction_merge_gff_output/")

#if not os.path.exists(args.o + "gene_prediction_combineall/"):
        #os.mkdir(args.o + "gene_prediction_combineall")

#if not os.path.exists(args.o + "gene_prediction_all_outputs/"):
        #os.mkdir(args.o + "gene_prediction_all_outputs/")

input_list=[]

for file in os.scandir(args.i):
	if file.path.endswith(".gff"):
		input_list.append(file.path)

x = os.listdir(args.i)

samples = []
 
for each in x:
	samples.append(each) 

#sorted_samples = []

#for each in y:
#	if each[0] == "C" and each [0:7] not in sorted_samples:
#		sorted_samples.append(each[0:7])

def sort(sorted_file):
	basename=(sorted_file.split("_"))[0]
	output_name=args.o + "sorted_gene_prediction/"
	if args.gm==True:
		os.system("bedtools sort -chrThenSizeD -i "+args.i + basename + "_meta_genemark.gff > "+ output_name + basename + "_meta_genemark_sorted.gff")
	if args.p==True:
		os.system("bedtools sort -chrThenSizeD -i "+args.i + basename + "_meta_prodigal.gff > "+ output_name + basename + "_meta_prodigal_sorted.gff")
	if args.gl==True:
		os.system("bedtools sort -chrThenSizeD -i "+args.i + basename + "_meta_glimmer.gff > "+ output_name + basename + "_meta_glimmer_sorted.gff")



def merge(gff_file):
	basename=(gff_file.split("_"))[0]
	input_name=args.o + "sorted_gene_prediction/"
	output_name=args.o + "final_gene_prediction_output/"

#intersect of all three
	if args.gm==True and args.p==True and args.gl==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_meta_prodigal_sorted.gff -b "+ input_name + basename + "_meta_genemark_sorted.gff " + input_name + basename + "_meta_glimmer_sorted.gff > "+ output_name + basename + "_final.gff")
	
#intersect of prodigal and genemark only
	elif args.p==True and args.gm==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_meta_prodigal_sorted.gff -b "+ input_name + basename + "_meta_genemark_sorted.gff > " + output_name + basename + "_final.gff")


#intersect of glimmer and genemark only
	elif args.gl==True and args.gm==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_meta_glimmer_sorted.gff -b "+ input_name + basename + "_meta_genemark_sorted.gff > "+ output_name + basename + "_final.gff")

		
#intersect of glimmer and prodigal only
	elif args.gl==True and args.p==True:
		os.system("bedtools intersect -f 1.0 -r -a " + input_name + basename + "_meta_prodigal_sorted.gff -b "+ input_name + basename + "_meta_glimmer_sorted.gff > "+ output_name + basename + "_final.gff")

#prodigal only
	elif args.p==True:
		shutil.copy(input_name + basename + "_meta_prodigal_sorted.gff", output_name + basename + "_final.gff")

#genemark only
	elif args.gm==True:
		shutil.copy(input_name + basename + "_meta_genemark_sorted.gff", output_name + basename + "_final.gff")	

#glimmer only
	elif args.gl==True:
		shutil.copy(input_name + basename + "_meta_glimmer_sorted.gff", output_name + basename + "_final.gff")
#generate fasta
	os.system("bedtools getfasta -fi " + args.f + " -bed " + output_name + basename + "_final.gff -fo "+ output_name + basename + "_final.fna")

#generate faa file
	os.system("transeq -sequence "+ output_name + basename + "_final.fna -outseq "+ output_name + basename + "_final.faa")

#os.system("tail -n +7 " + args.o + "gff_output/" + basename + "_meta_rnammer.gff | head -n -1 > " + args.o + "gene_prediction_combineall/" +  basename + "_combineall.gff")
	#os.system("cat " + args.o + "gff_output/" + basename + "_meta_aragorn.gff >> " + args.o + "gene_prediction_combineall/" +  basename + "_combineall.gff")

	#os.system("cat " + output_name + basename + "intersect_three.gff >> " + args.o + "gene_prediction_combineall/" +  basename + "_combineall.gff | bedtools sort -chrThenSizeD -i "  + args.o + "gene_prediction_combineall/" +  basename + "_combineall.gff > "  + args.o + "gene_prediction_all_outputs/" +  basename + "_final.gff")
 
#generate fasta
		#os.system("bedtools getfasta -fi " + args.f + basename + "_meta.gam.fasta -bed "+ output_name + basename + "intersect_three.gff -fo "+ output_name + basename + "intersect_three.fna")
	#os.system("bedtools getfasta -fi " + args.f + basename + "_meta.gam.fasta -bed " + args.o + "gene_prediction_all_outputs/" +  basename + "_final.gff -fo " + args.o + "gene_prediction_all_outputs/" + basename + "_final.fna")

#generate faa file
		#os.system("transeq -sequence "+ output_name + basename + "intersect_three.fna -outseq "+ output_name + basename + "intersect_three.faa")
	#os.system("transeq -sequence " + args.o + "gene_prediction_all_outputs/" + basename + "_final.fna -outseq " + args.o + "gene_prediction_all_outputs/" + basename + "_final.faa")

#individual genes
#	os.system("bedtools intersect -f 1.0 -r -v -a " + args.i2 + basename + "_meta_prodigal_sorted.gff -b "+ args.i2 + basename + "_meta_genemark_sorted.gff " + args.i2 + basename + "_meta_glimmer_sorted.gff > "+ args.o + basename + "prodigal_only.gff")
#	os.system("bedtools intersect -f 1.0 -r -v -a " + args.i2 + basename + "_meta_glimmer_sorted.gff -b "+ args.i2 + basename + "_meta_genemark_sorted.gff " + args.i2 + basename + "_meta_prodigal_sorted.gff > "+ args.o + basename + "glimmer_only.gff")
#	os.system("bedtools intersect -f 1.0 -r -v -a " + args.i2 + basename + "_meta_genemark_sorted.gff -b "+ args.i2 + basename + "_meta_glimmer_sorted.gff " + args.i2 + basename + "_meta_prodigal_sorted.gff > "+ args.o + basename + "genemark_only.gff")

#intersect of prodigal and genemark only
#	os.system("bedtools intersect -f 1.0 -r -a " + args.i2 + basename + "_meta_genemark_sorted.gff -b "+ args.i2 + basename + "_meta_prodigal_sorted.gff > "+ args.i3 + basename + "genemark_prodigal_total.gff")

#	os.system("bedtools intersect -f 1.0 -r -v -a " + args.i3 + basename + "genemark_prodigal_total.gff -b "+ args.i3 + basename + "intersect_three.gff > "+ args.o + basename + "genemark_prodigal_only.gff")

#intersect of glimmer and genemark only
#	os.system("bedtools intersect -f 1.0 -r -a " + args.i2 + basename + "_meta_genemark_sorted.gff -b "+ args.i2 + basename + "_meta_glimmer_sorted.gff > "+ args.i3 + basename + "genemark_glimmer_total.gff")
#	os.system("bedtools intersect -f 1.0 -r -v -a " + args.i3 + basename + "genemark_glimmer_total.gff -b "+ args.i3 + basename + "intersect_three.gff > "+ args.o + basename + "genemark_glimmer_only.gff")

#intersect of glimmer and prodigal only
#	os.system("bedtools intersect -f 1.0 -r -a " + args.i2 + basename + "_meta_prodigal_sorted.gff -b "+ args.i2 + basename + "_meta_glimmer_sorted.gff > "+ args.i3 + basename + "prodigal_glimmer_total.gff")
#	os.system("bedtools intersect -f 1.0 -r -v -a " + args.i3 + basename + "prodigal_glimmer_total.gff -b "+ args.i3 + basename + "intersect_three.gff > "+ args.o + basename + "prodigal_glimmer_only.gff")

for i in samples:
	sort(i)

y = os.listdir(args.o + "sorted_gene_prediction/")

sorted_samples = []

for each in y:
        if each not in sorted_samples:
                sorted_samples.append(each)

for k in sorted_samples:
	merge(k)
#For #generate fasta, the variable "fasta_file" is from the pipeline where it draws from genome assembly file names
