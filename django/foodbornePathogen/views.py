from copy import deepcopy
from collections import namedtuple
from threading import Thread
import subprocess as sp
from subprocess import PIPE
import logging
import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEText import MIMEText
#from email.MIMEBase import MIMEBase
#from email import encoders

from .models import *
from .forms import *

logger = logging.getLogger("django")  # /projects/team-1/django/django.log

BASE_URL = settings.BASE_URL
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL
SCRIPTS_ROOT = '/projects/team-1/src'

temp = [f'{STAGES[first]}-{STAGES[last]}' for first, last in RANGES]
rc = zip(temp, RANGE_CHOICES)
CONTEXT = {'range_choices': rc,
           'BASE_URL': BASE_URL}

STAGELIST = [GAStage, GPStage, FAStage, CGStage]
STAGEFORMLIST = [GAStageForm, GPStageForm, FAStageForm, CGStageForm]
MESSAGE = "Thank you for submitting your job to the Spring 2021 Computational Genomics Team 1 Foodborne Pathogen Predictive Webserver.\n\n" \
          "You're job has been completed. Results can be viewed at:\n\n" \
          "%sresults/%s\n\n" \
          "Thank you,\n" \
          "BIOL 7210 Team 1"


#def send_email(link, email):
#    msg = MIMEText('Your results from RASP-E are ready and can be accessed at: ' + str(link))
#    msg['From'] = 'gatech-bioinfo@biopredict2021.edu'
#    msg['To'] = email
#    msg['Subject'] = 'Georgia Tech Bioinfo Results'
#    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
#    # Both Python 2.X and 3.X
#    p.communicate(msg.as_bytes() if sys.version_info >= (3,0) else msg.as_string())

    
def run_bash_command_in_different_env(command, env):
    logger.info("Running Bash Command: " + str(command))
    
    full_command = 'bash -c ' \
        ' "source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh; ' \
        ' conda activate ' \
        + env + ' ; ' \
        + command + ' >> /projects/team-1/logs/django_pipeline.log"'
    logger.info("Full Python Subprocess Command: " + str(full_command))

    out = sp.run(full_command, shell=True)
    logger.info("Subprocess Log: " + str(out))


def get_client_args(params, stage):
    options = stage._meta.get_fields(include_parents=False)
    args = []
    for option in options:
        if option.name in params:
            if isinstance(params[option.name], bool):
                if params[option.name]:
                    args.append(f'-{PARAMETER_ABBREVS[option.name]}')
            else:
                args.append(f'-{PARAMETER_ABBREVS[option.name]}')
                args.append(params[option.name])
    return args


def run_job(clientEmail, job, params):
    logger.info('------------ run_job(clientEmail, files, job, params) -----------')
    logger.info('clientEmail = ' + clientEmail)
    logger.info('job.id = ' + str(job.id))
    logger.info('job.pipeRange = ' + str(job.pipeRange))

    # send_email("link", clientEmail)

    # Determine job characteristics
    pr = job.pipeRange
    first, last = RANGES[pr]
    runFlags = [False]*4
    for stage in range(first, last+1):
        runFlags[stage] = True
    samples = Sample.objects.filter(job=job.id)
    isolates = []
    for sample in samples:
        isolates.append(Isolate.objects.get(id=sample.id))

    # Run job stages
    if runFlags[0]:
        logger.info("Genome Assembly Pipeline Selected")

        # Database changes
        for isolate in isolates:
            isolate.seqReadsAvailable = True

        # Select sample set
        os.mkdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        for isolate in isolates:
            logger.info(f"Move GA input********************: {MEDIA_ROOT}{clientEmail}/{isolate}.zip --> /sample")
            os.link(f'{MEDIA_ROOT}{clientEmail}/{isolate}.zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip')

        # Call stage script
        args = get_client_args(params, GAStage)
        args.append(f'{MEDIA_ROOT}{clientEmail}/sample/')
        # sp.run(['/home/taylor/Desktop/class/BIOL7210/Team1-PredictiveWebServer/fake_genome_assembly_slim.sh'] + args)
        # cmd = f'{SCRIPTS_ROOT}/genome_assembly/fake_genome_assembly_slim.sh {" ".join(args)}'  # Uncomment for testing
        logger.info(f"GA run args*********************** {args}")
        cmd = f'{SCRIPTS_ROOT}/genome_assembly/genome_assembly_slim.sh {" ".join(args)}'  # TODO Uncomment for app deployment
        run_bash_command_in_different_env(cmd, 'genome_assembly')

        # Clean up junk files
        outputs = []
        for isolate in isolates:
            logger.info(f"Link outputs out parent folder: ***********************{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta --> ..")
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}.fasta')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.html', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}.html')
            outputs.append(f'{job.id}_{isolate}.fasta')
            outputs.append(f'{job.id}_{isolate}.html')
        #sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])
        os.chdir(f'{MEDIA_ROOT}{clientEmail}')
        logger.info(f"Zip GA outputs******************{MEDIA_ROOT}{clientEmail}/GA_{job.id}.zip <-- {outputs}")
        sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/GA_{job.id}.zip'] + outputs)

        # Database changes
        for isolate in isolates:
            isolate.assembliesAvailable = True

        logger.info("Genome Assembly Pipeline Done...")

    if runFlags[1]:
        logger.info("Gene Prediction Pipeline Selected")

        # Select sample set
        os.mkdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        for isolate in isolates:
            logger.info(f'Link GP inputs to sample folder*************************{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FASTA"] else str(job.id) + "_"}{isolate}.fasta')
            os.link(f'{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FASTA"] else str(job.id) + "_"}{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta')
            logger.info(f'Zip file inputs:**************************{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta --> {MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip')
            sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta'])

        # Call stage script
        args = get_client_args(params, GPStage)
        args = ['-i', f'{MEDIA_ROOT}{clientEmail}/sample/',
                '-o', f'{MEDIA_ROOT}{clientEmail}/sample/',
                '-t', '4'] + args
        # sp.run(['/home/taylor/Desktop/class/BIOL7210/Team1-PredictiveWebServer/fake_gene_prediction_master.py'] + args)
        #cmd = f'{SCRIPTS_ROOT}/gene_prediction/src/fake_gene_prediction_master.py {" ".join(args)}'  # Uncomment for testing
        cmd = f'{SCRIPTS_ROOT}/gene_prediction/src/gene_prediction_master.py {" ".join(args)}'  # TODO Uncomment for app deployment
        logger.info(f'Call script with args:**********************{args}')
        run_bash_command_in_different_env(cmd, 'gene_prediction')

        # Clean up junk files
        outputs = []
        for isolate in isolates:
            logger.info(f'Select outputs from sample folder:****************************{MEDIA_ROOT}{clientEmail}/sample/{isolate}_gp.gff -> {MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_gp.gff')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}_gp.faa', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_gp.faa')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}_gp.fna', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_gp.fna')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}_gp.gff', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_gp.gff')
            outputs.append(f'{job.id}_{isolate}_gp.faa')
            outputs.append(f'{job.id}_{isolate}_gp.fna')
            outputs.append(f'{job.id}_{isolate}_gp.gff')
        sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])
        os.chdir(f'{MEDIA_ROOT}{clientEmail}')
        logger.info(f'Zip output files************************{MEDIA_ROOT}{clientEmail}/GP_{job.id}.zip <-- {outputs}')
        sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/GP_{job.id}'] + outputs)

        # Database changes
        for isolate in isolates:
            isolate.genesAvailable = True

        logger.info("Gene Prediction Pipeline Done...")

    if runFlags[2]:
        logger.info("Functional Annotation Pipeline Selected")

        # Select sample set
        os.mkdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        for isolate in isolates:
            logger.info(f'Hardlink FA inputs into sample:*****************{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FASTA"] else str(job.id) + "_"}{isolate}.fasta --> {MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta')
            os.link(f'{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FASTA"] else str(job.id) + "_"}{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta')
            os.link(f'{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FAA"] else str(job.id) + "_"}{isolate}{"" if RANGE_INPUTS[pr]["FAA"] else "_gp"}.faa', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.faa')
            os.chdir(f'{MEDIA_ROOT}{clientEmail}/sample/')  # Prevent saving directory structure into zip
            logger.info(f'Zip file inputs:****************{MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip  <-- {isolate}.fasta, {isolate}.faa')
            sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip',
                    f'{isolate}.fasta',
                    f'{isolate}.faa'])

        # Call stage script
        args = get_client_args(params, FAStage)
        args = ['-I', f'{MEDIA_ROOT}{clientEmail}/sample/',
                '-O', f'{MEDIA_ROOT}{clientEmail}/sample/',
                '-u', '/projects/team-1/tools/functional_annotation/usearch11.0.667_i86linux32',
                '-D', '/projects/team-1/tools/functional_annotation/deeparg_database'] + args
        # sp.run(['/home/taylor/Desktop/class/BIOL7210/Team1-PredictiveWebServer/fake_functional_annotation_combined.py'] + args)
        #cmd = f'{SCRIPTS_ROOT}/functional_annotation/fake_functional_annotation_combined.py {" ".join(args)}'  # Uncomment for testing
        logger.info(f'Run FA script with args:***************** {args}')
        cmd = f'{SCRIPTS_ROOT}/functional_annotation/functional_annotation_combined.py {" ".join(args)}'  # TODO Uncomment for app deployment
        cenv = 'functional_annotation_deeparg' if '-D' in args else 'functional_annotation'
        run_bash_command_in_different_env(cmd, cenv)

        # Clean up junk files
        outputs = []
        for isolate in isolates:
            logger.info(f'Link FA output files to parent folder:************** {MEDIA_ROOT}{clientEmail}/sample/{isolate}_fa.gff --> {MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_fa.gff')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}_fa.gff', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_fa.gff')
            outputs.append(f'{job.id}_{isolate}_fa.gff')
        sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])
        os.chdir(f'{MEDIA_ROOT}{clientEmail}')
        logger.info(f'Zip FA outputs into download package:************{MEDIA_ROOT}{clientEmail}/FA_{job.id} <-- {outputs}')
        sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/FA_{job.id}'] + outputs)

        for isolate in isolates:
            isolate.annotationsAvailable = True

        logger.info("Functional Annotation Pipeline Done...")

    if runFlags[3]:
        logger.info("Comparative Genomics Pipeline Selected")

        # Select sample set
        os.mkdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        os.chdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        for isolate in isolates:
            inputs = []
            if params['run_ANIm'] or params['run_parSNP'] or params['get_virulence_factors']:
                logger.info(f'Move CG input FASTA to sample:************:{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FASTA"] else str(job.id) + "_"}{isolate}.fasta --> {MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta')
                inputs.append(f'{isolate}.fasta')
                os.link(f'{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FASTA"] else str(job.id) + "_"}{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta')
            if params['get_resistance_factors']:
                logger.info(f'Move CG input GFF to sample:************:{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["GFF"] else str(job.id) + "_"}{isolate}{"" if RANGE_INPUTS[pr]["GFF"] else "_fa"}.gff --> {MEDIA_ROOT}{clientEmail}/sample/{isolate}.gff')
                inputs.append(f'{isolate}.gff')
                os.link(f'{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["GFF"] else str(job.id) + "_"}{isolate}{"" if RANGE_INPUTS[pr]["GFF"] else "_fa"}.gff', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.gff')
            if params['run_stringMLST']:
                logger.info(f'Move CG input FQ to sample:************:{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FQ"] else str(job.id) + "_"}{isolate}.zip --> {MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip')
                inputs.append(f'{isolate}.zip')
                os.link(f'{MEDIA_ROOT}{clientEmail}/{"" if RANGE_INPUTS[pr]["FQ"] else str(job.id) + "_"}{isolate}.zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip')
            logger.info(f'Zipping CG inputs:********************* {MEDIA_ROOT}{clientEmail}/sample/{isolate}_.zip  <-- {inputs}')
            sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}_.zip'] + inputs)
            logger.info(f'Renaming zipped CG inputs:******************* {MEDIA_ROOT}{clientEmail}/sample/{isolate}_.zip <-- {MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip')
            os.rename(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}_.zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip')

        # Call stage script
        args = get_client_args(params, CGStage)
        args = args + ['-a', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-O', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-o', str(job.id),
                       '-r', '/projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/camplo_ref.fna']
        # sp.run(['/home/taylor/Desktop/class/BIOL7210/Team1-PredictiveWebServer/fake_Comparative_master_pipeline.sh'] + args)
        # cmd = f'{SCRIPTS_ROOT}/comparative_genomics/Team1-ComparativeGenomics/fake_Comparative_master_pipeline.sh {" ".join(args)}'  # Uncomment for testing
        logger.info(f'Running CG script with args:***************** {args}')
        cmd = f'{SCRIPTS_ROOT}/comparative_genomics/Team1-ComparativeGenomics/Comparative_master_pipeline.sh {" ".join(args)}'  # TODO Uncomment for app deployment
        run_bash_command_in_different_env(cmd, 'comparative_genomics')

        # Clean up junk files
        if params['run_ANIm']:
            logger.info(f'Hardlink ANI to parent dir:********************* {MEDIA_ROOT}{clientEmail}/sample/ANIm_percentage_identity.png --> {MEDIA_ROOT}{clientEmail}/ANIm_percentage_identity_{job.id}.png')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/ANIm_percentage_identity.png', f'{MEDIA_ROOT}{clientEmail}/ANIm_percentage_identity_{job.id}.png')
        if params['run_stringMLST']:
            logger.info(f'Hardlink MLST to parent dir:********************* {MEDIA_ROOT}{clientEmail}/sample/MLSTtree_{job.id}.pdf --> {MEDIA_ROOT}{clientEmail}/MLSTtree_{job.id}.pdf')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/MLSTtree_{job.id}.pdf', f'{MEDIA_ROOT}{clientEmail}/MLSTtree_{job.id}.pdf')
        if params['run_parSNP']:
            logger.info(f'Hardlink SNP to parent dir:********************* {MEDIA_ROOT}{clientEmail}/sample/SNP_{job.id}.pdf --> {MEDIA_ROOT}{clientEmail}/SNP_{job.id}.pdf')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/SNP_{job.id}.pdf', f'{MEDIA_ROOT}{clientEmail}/SNP_{job.id}.pdf')
        if params['get_resistance_factors']:
            logger.info(f'Hardlink resis_table to parent dir:********************* {MEDIA_ROOT}{clientEmail}/sample/res_table_{job.id}.png --> {MEDIA_ROOT}{clientEmail}/res_table_{job.id}.png{MEDIA_ROOT}{clientEmail}/res_table_{job.id}.png')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/res_table_{job.id}.png', f'{MEDIA_ROOT}{clientEmail}/res_table_{job.id}.png')
        if params['get_virulence_factors']:
            logger.info(f'Hardlink VF_table to parent dir:********************* {MEDIA_ROOT}{clientEmail}/sample/VF_table_{job.id}.png --> {MEDIA_ROOT}{clientEmail}/VF_table_{job.id}.png')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/VF_table_{job.id}.png', f'{MEDIA_ROOT}{clientEmail}/VF_table_{job.id}.png')
        sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])

        logger.info("Comparative Genomics Pipeline Done...")

    for isolate in isolates:
        isolate.save()

    # Contact user  TODO Figure out how to send email; Alternative is just to print out the link on results.
    # send_mail("Foodborn Pathogen job completed", MESSAGE.format(BASE_URL, job.id), from_email=None, recipient_list=[clientEmail])


def index(request):
    context = deepcopy(CONTEXT)
    return render(request, 'foodbornePathogen/index.html', context)


def terms(request):
    context = deepcopy(CONTEXT)
    return render(request, 'foodbornePathogen/terms.html', context)


def options(request, **kwargs):
    first, last = kwargs['range_choice'].split('-')
    first, last = int(STAGE_INDS[first]), int(STAGE_INDS[last])
    if request.method == 'GET':
        # get baseline context
        context = deepcopy(CONTEXT)

        # give user form to context
        context['user'] = UserForm()

        # give upload form to context
        context['upload'] = UploadForm()

        # give stages forms to context
        StageTup = namedtuple('StageTup', ['name', 'form'])
        context['stages'] = [StageTup(STAGES[i], STAGEFORMLIST[i]()) for i in range(first, last + 1)]

        return render(request, 'foodbornePathogen/options.html', context)

    elif request.method == 'POST':
        # Make/get user
        userEmail = request.POST['email']
        try:
            user = User.objects.get(email=userEmail)
        except ObjectDoesNotExist:
            user = User(email=userEmail)
            user.save()

        # Make job
        first, last = kwargs['range_choice'].split('-')
        first, last = STAGE_INDS[first], STAGE_INDS[last]
        pipeRange = RANGES_INDS[(first, last)]
        job = Job(user=user, pipeRange=pipeRange)
        job.save()

        # Make isolates & samples
        for file in request.FILES.getlist('upload'):
            isolate = Isolate(user=user, upload=file)
            isolate.save()
            os.makedirs(f'{MEDIA_ROOT}{userEmail}/', exist_ok=True)
            os.rename(f'{MEDIA_ROOT}{isolate.upload}', f'{MEDIA_ROOT}{userEmail}/{isolate.upload}.zip')  # Extension & user folder are removed in file saving, so must be restored
            if first:  # If requested job does not start with genome assembly (i.e. uploaded files are not reads), unzip uploads
                os.rename(f'{MEDIA_ROOT}{userEmail}/{isolate.upload}.zip', f'{MEDIA_ROOT}{userEmail}/{isolate.upload}_.zip')
                sp.run(['unzip', '-d', f'{MEDIA_ROOT}{userEmail}/', f'{MEDIA_ROOT}{userEmail}/{isolate.upload}_.zip'])  # Assume client has given same filenames to contents as outer TODO Eliminate assumption
                os.remove(f'{MEDIA_ROOT}{userEmail}/{isolate.upload}_.zip')
            sample = Sample(isolate=isolate, job=job)
            sample.save()

        # Make stages
        for i in range(first, last+1):
            params = {}
            for attr in STAGELIST[i]._meta.get_fields(include_parents=False):
                if isinstance(attr, models.BooleanField):
                    if attr.name in request.POST:
                        params[attr.name] = True
                    else:
                        params[attr.name] = False
                else:
                    if attr.name in request.POST:
                        params[attr.name] = request.POST[attr.name]
            stage = STAGELIST[i](job=job, **params)
            stage.save()

        # Begin the job
        newJob = Thread(target=run_job, args=(userEmail, job, params))
        newJob.start()

        return HttpResponseRedirect(f'/fbp/submitted/{job}')


def submitted(request, **kwargs):
    context = deepcopy(CONTEXT)
    context['job_id'] = kwargs['job_id']
    context['userEmail'] = Job.objects.get(id=kwargs['job_id']).user.email
    return render(request, 'foodbornePathogen/submitted.html', context)


def info(request, **kwargs):
    context = deepcopy(CONTEXT)
    return render(request, 'foodbornePathogen/info.html', context)


def results(request, **kwargs):  # TODO Construct results page
    context = deepcopy(CONTEXT)
    context['userDir'] = f"{MEDIA_ROOT}{Job.objects.get(id=kwargs['job_id']).user.email}"
    context['jobID'] = kwargs['job_id']
    return render(request, 'foodbornePathogen/results.html', context)
