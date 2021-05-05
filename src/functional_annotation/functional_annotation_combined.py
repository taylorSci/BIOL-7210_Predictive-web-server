#/usr/bin/env python3
# -*- encoding: utf-8 -*-

###----------------------USAGE-------------------
#python functional_annotation_combined.py -I <Input Directory> -i <clustering identity (0.95 default)> -u <usearch executable path>  -E <eggnog database directory> -D <deeparg database directory> -n <genome assembly paired contigs fasta file directory> -O <output directory> -p 

##change I to input directory

##---------------IMPORTING PACKAGES---------------
import os
import subprocess
import optparse
import shutil
import zipfile

##---------------OPTIONS------------------
def opts():
    parser = optparse.OptionParser()
	
    parser.add_option('-I', '--input_directory', help = 'input protein sequence directory path', dest = 'I')
    parser.add_option('-i', '--identity', default = 0.95, help = 'clustering identity', dest = 'i')
    parser.add_option('-u', '--usearch_loc', help = 'usearch absolute path', dest = 'u')
    parser.add_option('-E', '--eggnog_database', help = 'eggnog database path', dest = 'E')
    parser.add_option('-D', '--deeparg_database', help = 'deeparg database path', dest = 'D')
    parser.add_option('-n', '--paired_contigs_directory', help = 'paired contigs directory path', dest = 'n')
    parser.add_option('-p', '--run_pilercr', action='store_false', dest= 'p')
    parser.add_option('-O', '--output_directory', help = 'output directory path', dest = 'O')
    return(parser.parse_args())

##--------------USEARCH-------------------

##usage: perform_usearch(input_path, input_files, clust_id, usearch_path, output_path)

def perform_usearch(inpath, filenames, identity, usearch_loc, outpath):

	##make clustering folder in outpath to put all outputs

	f_combined = open(outpath + '/clustering/combined_fasta.faa', 'w')
	for f in filenames:
		if '.faa' in f:
			current_file = open(inpath + '/' + f, 'r')
			for line in current_file:
				if line[0] == '>':
					name = '>' + f[:-4]+ '__' + line[1:]
					f_combined.write(name)
				else:
					f_combined.write(line)
			current_file.close()
	f_combined.close()
	
	##command: usearch_path -clusterfast outpath/clustering/comgined_fasta.faa -id str(identity) -centroids outpath/clustering/centroids.fa -uc outpath/clustering/seq_labels.uc
	command = [usearch_loc, '-cluster_fast', outpath + '/clustering/combined_fasta.faa', '-id', str(identity), '-centroids', outpath + '/clustering/centroids.fa', '-uc', outpath + '/clustering/seq_labels.uc']
	subprocess.run(command)


##-------------EGGNOG MAPPER-----------
#usage perform_eggnogmapper(output_path + '/clustering/centroids.fa', eggnog_database, 'eggnog', output_path + '/eggnog', 'bact', number of cpus)
def perform_eggnogmapper(centroids_file, data_directory, output_base, output_directory, cpu):
    # data_directory = is the path to where the database is
    # output_base is the output file name you want all your output files to have
    # output_directory = the path to where you want your outputs to go
    # database_type = is you are looking for bact, euk, arch
    command_to_run = ['emapper.py', '-i', centroids_file,  '-m', 'diamond', '--data_dir', data_directory, '--output', output_base, '--output_dir', output_directory, '--cpu', cpu]
    print(command_to_run)
    subprocess.run(command_to_run)

    ## format output to gff
    outputfilepath = output_directory + '/' + output_base + '.emapper.annotations'
    annotate_list = []
    with open(outputfilepath, 'r') as fh:
        for line in fh.readlines()[4:-3]:
            line = line.split("\t")
            query_name = line[0]
            ##this is the ortholog score
            ##if we want to include the e-value then we need line[2]
            score = line[2]
            ## common name of protein
            name = line[5]
            #gives a brief description about the query 
            attributes = line[21][:-2]
            annotate_list.append([query_name, score, name, attributes])
    ### assign to seqid of centroid
    gfffile = output_directory + '/eggnog_output.gff'
    fh1 = open(gfffile, 'w+')
    fh1.write("##gff-version file" + "\n")
    fh1.write("seqid" + '\t' + "source" +"\t" +"type"+"\t"+"start"+"\t"+"end"+"\t"+"score"+"\t"+"strand"+"\t"+"phase"+"\t"+"attributes"+"\n")
    for i in range(len(annotate_list)):
        x = annotate_list[i]
        query_name = x[0]
        ran = query_name.split('__')[1][:-2]
        ran = ran.split('-')
        start = ran[0]
        stop = ran[1]
        l = query_name + "\t" + "eggnog" + "\t" + "." + "\t" + start +"\t"+ stop +"\t"+ str(x[1]) +"\t"+"."+"\t"+"."+"\t"+ str(x[2]) +";"+ str(x[3])
        fh1.write(l + '\n')

###-----------DEEPARG----------
##usage: perform_deepARG(output_path + '/deeparg/deeparg')
def perform_deepARG(output_directory):
## format output to gff
	outputfilepath = output_directory + '.align.daa.tsv'
	annotate_list = []
	with open(outputfilepath, 'r') as fh:
		for line in fh.readlines()[4:-3]:
			line = line.strip()
			line = line.split("\t")
			query_name = line[0]
            		##this is the ortholog score
            		##if we want to include the e-value then we need line[2]
			score = line[10]
            		## antibiotic resistance gene info
			antibiotic_info = line[1]
			annotate_list.append([query_name, score, antibiotic_info])
    	### assign to seqid of centroid
	gfffile = output_directory + '_output.gff'
	fh1 = open(gfffile, 'w+')
	fh1.write("##gff-version file" + "\n")
	fh1.write("seqid" + '\t' + "source" +"\t" +"type"+"\t"+"start"+"\t"+"end"+"\t"+"score"+"\t"+"strand"+"\t"+"phase"+"\t"+"attributes"+"\n")
	for i in range(len(annotate_list)):
		x = annotate_list[i]
		query_name = x[0]
		ran=query_name.rsplit('-', 1)
		#ran = query_name.split('_')[0]
		#ran = ran[:-2]
		#ran = ran.split('-')
		start = (ran[0]).rsplit('_')[-1]
		stop = (ran[1]).rsplit('_')[0]
		l = query_name + "\t" + "DeepARG" + "\t" + "." + "\t" + start +"\t"+ stop +"\t"+ str(x[1]) +"\t"+"."+"\t"+"."+"\t"+ str(x[2])
		fh1.write(l + '\n')
        
##-----PILER-CR----------------
#usage: perform_pilercr(contigs_directory, output_path + '/pilercr')
def perform_pilercr(inputdirectory, outputdirectory):
    for i in os.listdir(inputdirectory):
        command = ['pilercr', '-in', inputdirectory +'/'+i,'-out', outputdirectory + '/pilercr/' + i[:-6]+'_pilercr_out.txt','-noinfo']
        subprocess.run(command)
    gff_file = open(outputdirectory + '/pilercr_combined.gff', 'w')
    gff_file.write('##gff-version3\n')
    gff_file.close()
    for filename in os.listdir(outputdirectory + '/pilercr'):
        pilercrout = open(outputdirectory + "/pilercr/" + filename)
        pilercr=[]
        for line in pilercrout:
            row = line.strip().split()
            pilercr.append(row)
        

        source="PILERCR"
        typ="CRISPR"
        score="."
        phase ="."
        attributes = "."
        if ['SUMMARY', 'BY', 'SIMILARITY'] not in  pilercr: 
            continue
        else:
            summary = (pilercr.index(['SUMMARY', 'BY', 'SIMILARITY']) + 6)

        for i in range(summary, len(pilercr)):
            if not pilercr[i]: 
                continue
            if pilercr[i][0].startswith("*"):
                continue
            if pilercr[i][0].startswith("SUMMARY"):
                break
            else:
                seqid = filename.split("_")[0] + "__" + pilercr[i][1]
                start= int(pilercr[i][2])
                end = start + int(pilercr[int(i)][3])
                strand = pilercr[i][7]
            with open(outputdirectory + '/pilercr_combined.gff', 'a') as f:
                f.write(seqid + "\t" + source + "\t" + typ + "\t" + str(start) + "\t" + str(end) + "\t" + score + "\t" + strand + "\t" + phase + "\t" + attributes + "\n")
            f.close()
        
##----BACKTRACKING AND WRITING TO GFF------------
#usage: centroid_matching(outpath+'/clustering/seq_labels.uc')
def centroid_matching(uc_file):
    print('Matching Sequences')
    centroid_matches = {}
    uc_clusters = open(uc_file, 'r')
    for line in uc_clusters:
        line = line.split('\t')
        centroid = line[9]
        sequence = line[8]
        if '*' in centroid:
            centroid = line[8]
        centroid = centroid.strip()
        sequence = sequence.strip()
        if centroid not in centroid_matches.keys():
            centroid_matches[centroid] = [centroid]
        else:
            centroid_matches[centroid].append(sequence)
    return(centroid_matches)

##usage: create_gff_dict(clust_dict, gff_file_path)
def create_gff_dict(cluster_dict, combined_gff):
    gff_dict = {}
    gff_file = open(combined_gff, 'r')
    gff_file = gff_file.readlines()
    for line in gff_file[1:]:
        line = line.strip()
        centroid_name = line.split('\t')[0]
        annotation = line.split('\t')[1:]
        for seq in cluster_dict[centroid_name]:
            if annotation[0] == 'eggnog' or annotation[0] == 'DeepARG':
                range = seq.split('__')[1][:-2]
                range = range.split('-')
                start = range[0]
                stop = range[1]
                annotationstring = seq + "\t" + annotation[0] + "\t" + annotation[1] + "\t" + start +"\t"+ stop +"\t"+ annotation[4] +"\t"+annotation[5]+"\t"+annotation[6]+"\t"+ annotation[7]
            if seq in gff_dict:
                 gff_dict[seq].append(annotationstring)
            else:
                gff_dict[seq] = [annotationstring]
    return(gff_dict)

##usage: write_gff_files(seq_list, gff_dict, outpath+ '/merged_gff')
def write_gff_files(sequence_list, gff_mapped, output):
    for seq in sequence_list:
        gff_file = open(output + '/' + seq + '_fa.gff', 'w+')
        gff_file.write('##gff-version 3\n')
        for query in gff_mapped.keys():
            query_seq = query.split('__')[0]
            if seq == query_seq:
                for annotation in gff_mapped[query]:
                    gff_file.write(annotation + '\n')
                    
##usage: add_pilecr(seq_list, outpath + '/merged_gff', pilecr_gff_path)                    
def add_pilecr(sequence_list, output, pilecr_gff):
    gff_list = os.listdir(output)
    pilecr_file = open(pilecr_gff, 'r')
    pilecr_file = pilecr_file.readlines()
    for line in pilecr_file[1:]:
        line = line.strip()
        annotation = 'P' + line.rsplit('Paired', 1)[1]
        seq_name = (line.rsplit('Paired')[0]).rsplit("_")[0] 
        for gff_name in gff_list:
            if seq_name in gff_name:
                file = open(output + '/' + gff_name, 'a')
                file.write(annotation + '\n')
                
###----ANNOTATE FASTA---------------
#usage annotate_faa_files(output_path + '/merged_gff', gff_list, input_path, contigs_directory, output_path + '/annotated_fasta')
def annotate_faa_files(gff_directory, gff_list, faa_directory, fna_directory, output):
    print('Annotating .faa files')
    for gff_file in gff_list:
        gfffile = open(gff_directory + '/' + gff_file, 'r')
        print('annotating ' + gff_file)
        for line in gfffile.readlines()[1:]:
            line = line.strip()
            line = line.split('\t')
            if line[1] == 'PILERCR':
                annotation = line[0] + '\t' + line[2] + '\n'
                sample_id = gff_file[:7]
                seq_id = line[0]
                nucleotide_file = open(fna_directory + '/' + sample_id + '_meta.gam.fasta', 'r')
                sequence = ''
                lines = nucleotide_file.readlines()
                length = len(lines)
                for i in range(length - 1):
                    nuc_line = lines[i]
                    if '>' in nuc_line and seq_id in nuc_line:
                        if i == length - 1:
                            sequence = nuc_line.strip()
                        else:
                            for j in range(i + 1 , length):
                                seq_line = lines[j]
                                if '>' in seq_line:
                                    break
                                else:
                                    seq_line = seq_line.strip()
                                    sequence = sequence + seq_line
                start = int(line[3]) -1
                stop = int(line[4]) -1
                sequence = sequence[start:stop]
                annotated_file = open(output + '/' + sample_id + '.fna', 'a+')
                annotated_file.write('>' + annotation)
                annotated_file.write(sequence + '\n')
            if line[1] == 'eggnog' or line[1] == 'DeepARG' or line[1] == 'blast':
                annotation = line[0] + '\t' + 'score=' + line[5] + ';' + line[8] + '\n'
                sample_id = line[0].split('__')[0]
                seq_id = line[0].split('__')[1]
                aa_file = open(faa_directory + '/' + sample_id + '.faa', 'r')
                sequence = ''
                lines = aa_file.readlines()
                length = len(lines)
                for i in range(length - 1):
                    aa_line = lines[i]
                    if '>' in aa_line and seq_id in aa_line:
                        if i == length - 1:
                            sequence = aa_line.strip()
                        else:
                            for j in range(i + 1 , length):
                                seq_line = lines[j]
                                if '>' in seq_line:
                                    break
                                else:
                                    seq_line = seq_line.strip()
                                    sequence = sequence + seq_line
                annotated_file = open(output + '/' + sample_id[:7] + '.faa', 'a+')
                annotated_file.write('>' + annotation)
                annotated_file.write(sequence + '\n')

##----------MAIN---------------
def main():
	options, args = opts()
	input_path = options.I
	for file in os.scandir(options.I):
        	if file.path.endswith(".zip"):
                	dest= (file.name).strip(".zip")
                	with zipfile.ZipFile(file, "r") as zip_ref:
                        	zip_ref.extractall(options.I)
                	for subfile in os.scandir(options.I + "/" + dest):
                        	shutil.copy2(subfile, options.I)
                	subprocess.call(["rm", "-r", options.I + "/" + (file.name).strip(".zip")])
			#subprocess.call(["rm", "-r", file])

	input_files =os.listdir(input_path)
	clust_id = options.i
	usearch_path = options.u
	output_path = options.O
	eggnog_database = options.E
	deeparg_database = options.D
	#contigs_directory = options.n
	run_pilercr= options.p
	if not os.path.exists(output_path + "/assembled_reads"):
                os.makedirs(output_path + "/assembled_reads")
	for file in os.scandir(input_path):
		if file.path.endswith(".fasta"):
			subprocess.call(["cp", file, output_path + "/assembled_reads/"])
		#if file.path.endswith(".faa"):
		#	input_files.append(file)
		
	contigs_directory = output_path + "/assembled_reads/"	

	##create temp directories
	if not os.path.exists(output_path):
		os.makedirs(output_path)
	if not os.path.exists(output_path + '/clustering'):
		os.makedirs(output_path + '/clustering')
	if not os.path.exists(output_path + '/eggnog'):
		os.makedirs(output_path + '/eggnog')
	if not os.path.exists(output_path+ '/deeparg'):
		os.makedirs(output_path + '/deeparg')
	if not os.path.exists(output_path+ '/pilercr'):
		os.makedirs(output_path + '/pilercr')
	if not os.path.exists(output_path + '/merged_gff'):
		os.makedirs(output_path + '/merged_gff')

	#input_list=[]
	#for file in os.scandir(options.I):
	#	if file.path.endswith(".faa"):
	#		input_list.append(file.path)
	#for file in input_list: 
	#	basename=os.path.basename(file)
	#	basename=basename.replace("_gp.faa", "")
	#	basename=basename.replace(".faa", "")
	### run pipeline
	print('Clustering protein sequences...')
	perform_usearch(input_path, input_files, clust_id, usearch_path, output_path)
	if eggnog_database is not None: 
		print('Performing eggnog mapper...')
		perform_eggnogmapper(input_path + '/clustering/centroids.fa', eggnog_database, 'eggnog', output_path + '/eggnog', '3')
	if deeparg_database is not None:
		print('Changing to deeparg conda environment...')
		deeparg_command = 'deeparg predict -i ' + input_path + '/clustering/centroids.fa' + ' --model SS -o ' + output_path + '/deeparg/deeparg -d ' + deeparg_database + ' --type prot --min-prob 0.8'
		deeparg_bash = 'bash -c "source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh; conda activate functional_annotation_deeparg; '+ deeparg_command + '"'
		print('Changing to python 2.7 environment and performing deeparg')
		conda_change = subprocess.call(deeparg_bash, shell = True) ##activate python 2.7 environment
		perform_deepARG(output_path + '/deeparg/deeparg')
	if options.p==True:
		print('Performing pilercr...')
		perform_pilercr(contigs_directory, output_path)
	print('Backtracking and merging gff files...')
	combined = open(output_path + '/combined_outputs.gcc', 'w')
	combined.write('##gff-version3\n')
	combined.close()
	if eggnog_database is not None:
		os.system('tail -n+3 ' + output_path + '/eggnog/eggnog_output.gff >> ' + output_path + '/combined_outputs.gff')
	if deeparg_database is not None:
		os.system('tail -n+3 ' + output_path + '/deeparg/deeparg_output.gff >> ' + output_path + '/combined_outputs.gff')
	clust_dict = centroid_matching(output_path + '/clustering/seq_labels.uc')
	gff_dict = create_gff_dict(clust_dict, output_path + '/combined_outputs.gff')
	seq_list = []
	for f in input_files:
		if '.faa' in f:
			seq_list.append(f[:-4])
	write_gff_files(seq_list, gff_dict, output_path + '/merged_gff')
	if run_pilercr==True:
		add_pilecr(seq_list, output_path + '/merged_gff', output_path + '/pilercr_combined.gff')
        #print('Annotating fasta files...')
        #gff_list = os.listdir(output_path + '/merged_gff')
        #annotate_faa_files(output_path + '/merged_gff', gff_list, input_path, contigs_directory, output_path + '/annotated_fasta')
	#remove subdirectories
	for file in os.scandir(input_path + "/merged_gff/"):
		shutil.move(file.path, input_path)
		
	subprocess.call(["rm", "-r", output_path + '/clustering/'])
	subprocess.call(["rm", "-r", output_path + '/eggnog/'])
	subprocess.call(["rm", "-r", output_path + '/pilercr/'])
	subprocess.call(["rmdir", output_path + '/merged_gff/'])
	subprocess.call(["rm", "-r", output_path + '/deeparg/'])
	print('----Pipeline Complete----')
    


if __name__ == '__main__':
	main()
