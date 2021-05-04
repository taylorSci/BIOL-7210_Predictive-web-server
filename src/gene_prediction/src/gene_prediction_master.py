#!/projects/team-1/devops/anaconda3/envs/gene_prediction/bin/python3

import argparse
import subprocess
import os


parser=argparse.ArgumentParser(description='example: ./gene_prediction_master.py -i /home/team1/genome_assembly/output/assembly-reconciliation/ -t 5 -o /home/scleland7/')
parser.add_argument("-i", required=True, help="full path to input folder with fasta files")
parser.add_argument("-t", default=1, help="Number of threads")
parser.add_argument("-o", required=True, help="full path to output folder")
parser.add_argument("-a", action="store_true", help="run aragorn")
parser.add_argument("-r", action="store_true", help="run rnammer")
parser.add_argument("-p", action="store_true", help="run prodigal")
parser.add_argument("-gm", action="store_true", help="run genemark")
parser.add_argument("-gl", action="store_true", help="run glimmer")
args=parser.parse_args()

gff_output= args.o + "/gene_prediction_output/gff_output/"
prediction_script="/projects/team-1/src/gene_prediction/src/gene_prediction_pipeline.py"
merge_script="/projects/team-1/src/gene_prediction/src/merge.py"

if args.gm==True and args.p==True and args.gl==True:
	subprocess.call([prediction_script, "-i", args.i, "-t", args.t, "-o", args.o, "-gm", "-p", "-gl"])
	subprocess.call([merge_script, "-i", gff_output, "-f", args.i, "-o", args.o, "-gm", "-p", "-gl"])

elif args.p==True and args.gm==True:
	subprocess.call([prediction_script, "-i", args.i, "-t", args.t, "-o", args.o, "-gm", "-p"])
	subprocess.call([merge_script, "-i", gff_output, "-f", args.i, "-o", args.o + "/gene_prediction_output/", "-gm", "-p"])

elif args.gl==True and args.gm==True:
	subprocess.call([prediction_script, "-i", args.i, "-t", args.t, "-o", args.o, "-gm", "-gl"])
	subprocess.call([merge_script, "-i", gff_output, "-f", args.i, "-o", args.o + "/gene_prediction_output/", "-gm", "-gl"])

elif args.gl==True and args.p==True:
	subprocess.call([prediction_script, "-i", args.i, "-t", args.t, "-o", args.o, "-p", "-gl"])
	subprocess.call([merge_script, "-i", gff_output, "-f", args.i, "-o", args.o + "/gene_prediction_output/", "-p", "-gl"])

elif args.p==True:
	subprocess.call([prediction_script, "-i", args.i, "-t", args.t, "-o", args.o, "-p"])
	subprocess.call([merge_script, "-i", gff_output, "-f", args.i, "-o", args.o, "-p"])

elif args.gl==True:
	subprocess.call([prediction_script, "-i", args.i, "-t", args.t, "-o", args.o, "-gl"])
	subprocess.call([merge_script, "-i", gff_output, "-f", args.i, "-o", args.o + "/gene_prediction_output/", "-gl"])

elif args.gm==True:
	subprocess.call([prediction_script, "-i", args.i, "-t", args.t, "-o", args.o, "-gm"])
	subprocess.call([merge_script, "-i", gff_output, "-f", args.i, "-o", args.o + "/gene_prediction_output/", "-gm"])

subprocess.call(["rm", "-r", args.o + "/gene_prediction_output/"])

