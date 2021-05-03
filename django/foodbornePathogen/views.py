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


def run_bash_command_in_different_env(command, env):
    logger.info("Running Bash Command: " + str(command))
    
    full_command = 'bash -c ' \
        ' "source /projects/team-1/devops/anaconda3/etc/profile.d/conda.sh; ' \
        ' conda activate ' \
        + env + ' ; ' \
        + command + ' "'
    logger.debug("Full Python Subprocess Command: " + str(full_command))

    out = sp.run(full_command, shell=True, stdout=sp.DEVNULL)
    logger.debug("Subprocess Log: " + str(out))


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
    logger.debug('clientEmail = ' + clientEmail)
    logger.debug('job.id = ' + str(job.id))
    logger.debug('job.pipeRange = ' + str(job.pipeRange))

    # Determine job characteristics
    first, last = RANGES[job.pipeRange]
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
            os.link(f'{MEDIA_ROOT}{clientEmail}/{isolate}.zip', f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.zip')

        # Call stage script
        args = get_client_args(params, GAStage)
        args.append(f'{MEDIA_ROOT}{clientEmail}/sample/')
        cmd = f'{SCRIPTS_ROOT}/genome_assembly/fake_genome_assembly_slim.sh {" ".join(args)}'  # Uncomment for testing
        # cmd = f'{SCRIPTS_ROOT}/genome_assembly/genome_assembly_slim.sh {" ".join(args)}'  # TODO Uncomment for app deployment
        run_bash_command_in_different_env(cmd, 'genome_assembly')

        # Clean up junk files
        for isolate in isolates:
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}.fasta')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{isolate}.html', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}.html')
        sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])

        # Database changes
        for isolate in isolates:
            isolate.assembliesAvailable = True

        logger.info("Genome Assembly Pipeline Done...")

    if runFlags[1]:
        logger.info("Gene Prediction Pipeline Selected")

        # Select sample set
        os.mkdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        filePrefix = '' if first == 1 else f'{job.id}_'
        for isolate in isolates:
            os.link(f'{MEDIA_ROOT}{clientEmail}/{filePrefix}{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.fasta')
            sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.zip', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.fasta'])

        # Call stage script
        args = get_client_args(params, GPStage)
        args = args + ['-i', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-o', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-t', '4']
        cmd = f'{SCRIPTS_ROOT}/gene_prediction/src/fake_gene_prediction_master.py {" ".join(args)}'  # Uncomment for testing
        # cmd = f'{SCRIPTS_ROOT}/gene_prediction/src/gene_prediction_master.py {" ".join(args)}'  # TODO Uncomment for app deployment
        run_bash_command_in_different_env(cmd, 'gene_prediction')

        # Clean up junk files
        for isolate in isolates:
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_gp.faa', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_gp.faa')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_gp.fna', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_gp.fna')
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_gp.gff', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_gp.gff')
        sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])

        # Database changes
        for isolate in isolates:
            isolate.genesAvailable = True

        logger.info("Gene Prediction Pipeline Done...")

    if runFlags[2]:
        logger.info("Functional Annotation Pipeline Selected")

        # Select sample set
        os.mkdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        filePrefix = '' if first == 2 else f'{job.id}_'
        for isolate in isolates:
            os.link(f'{MEDIA_ROOT}{clientEmail}/{filePrefix}{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.fasta')
            os.link(f'{MEDIA_ROOT}{clientEmail}/{filePrefix}{isolate}_gp.faa', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_gp.faa')
            sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.zip',
                    f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.fasta',
                    f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_gp.faa'])

        # Call stage script
        args = get_client_args(params, FAStage)
        args = args + ['-I', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-O', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-u', '/projects/team-1/tools/functional_annotation/usearch11.0.667_i86linux32',
                       '-D', '/projects/team-1/tools/functional_annotation/deeparg_database']
        cmd = f'{SCRIPTS_ROOT}/functional_annotation/fake_functional_annotation_combined.py {" ".join(args)}'  # Uncomment for testing
        # cmd = f'{SCRIPTS_ROOT}/functional_annotation/functional_annotation_combined.py {" ".join(args)}'  # TODO Uncomment for app deployment
        cenv = 'functional_annotation_deeparg' if '-D' in args else 'functional_annotation'
        run_bash_command_in_different_env(cmd, cenv)

        # Clean up junk files
        for isolate in isolates:
            os.link(f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_gp_fa.gff', f'{MEDIA_ROOT}{clientEmail}/{job.id}_{isolate}_fa.gff')
        sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])

        for isolate in isolates:
            isolate.annotationsAvailable = True

        logger.info("Functional Annotation Pipeline Done...")

    if runFlags[3]:
        logger.info("Comparative Genomics Pipeline Selected")

        # Select sample set
        os.mkdir(f'{MEDIA_ROOT}{clientEmail}/sample/')
        filePrefix = '' if first == 3 else f'{job.id}_'
        for isolate in isolates:
            os.link(f'{MEDIA_ROOT}{clientEmail}/{filePrefix}{isolate}.fasta', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.fasta')
            os.link(f'{MEDIA_ROOT}{clientEmail}/{filePrefix}{isolate}_fa.gff', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_fa.gff')
            os.link(f'{MEDIA_ROOT}{clientEmail}/{filePrefix}{isolate}.zip', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.zip')
            sp.run(['zip', f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.zip',
                    f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}.fasta',
                    f'{MEDIA_ROOT}{clientEmail}/sample/{filePrefix}{isolate}_fa.gff'])

        # Call stage script
        args = get_client_args(params, CGStage)
        args = args + ['-a', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-O', f'{MEDIA_ROOT}{clientEmail}/sample/',
                       '-o', job.id,
                       '-r', '/projects/team-1/src/comparative_genomics/Team1-ComparativeGenomics/camplo_ref.fna']
        cmd = f'{SCRIPTS_ROOT}/comparative_genomics/Team1-ComparativeGenomics/Comparative_master_pipeline.sh {" ".join(args)}'  # Uncomment for testing
        # cmd = f'{SCRIPTS_ROOT}/comparative_genomics/Team1-ComparativeGenomics/Comparative_master_pipeline.sh {" ".join(args)}'  # TODO Uncomment for app deployment
        run_bash_command_in_different_env(cmd, 'comparative_genomics')

        # Clean up junk files
        os.link(f'{MEDIA_ROOT}{clientEmail}/sample/ANIm_percentage_identity.png', f'{MEDIA_ROOT}{clientEmail}/ANIm_percentage_identity_{job.id}.png')
        os.link(f'{MEDIA_ROOT}{clientEmail}/sample/MLSTtree_{job.id}.pdf', f'{MEDIA_ROOT}{clientEmail}/MLSTtree_{job.id}.pdf')
        os.link(f'{MEDIA_ROOT}{clientEmail}/sample/SNP_{job.id}.pdf', f'{MEDIA_ROOT}{clientEmail}/SNP_{job.id}.pdf')
        os.link(f'{MEDIA_ROOT}{clientEmail}/sample/res_table_{job.id}.png', f'{MEDIA_ROOT}{clientEmail}/res_table_{job.id}.png')
        os.link(f'{MEDIA_ROOT}{clientEmail}/sample/VF_table_{job.id}.png', f'{MEDIA_ROOT}{clientEmail}/VF_table_{job.id}.png')
        sp.run(['rm', '-r', f'{MEDIA_ROOT}{clientEmail}/sample'])

        logger.info("Comparative Genomics Pipeline Done...")

    for isolate in isolates:
        isolate.save()

    # Contact user  TODO Figure out how to send email; Alternative is just to print out the link on results.
    send_mail("Foodborn Pathogen job completed", MESSAGE.format(BASE_URL, job.id), from_email=None, recipient_list=[clientEmail])


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
            sp.run(['mv', f'{MEDIA_ROOT}/{isolate.upload}', f'{MEDIA_ROOT}/{userEmail}/{isolate.upload}.zip'])  # Extension & user folder are removed in file saving, so must be restored
            if first:  # If requested job does not start with genome assembly (i.e. uploaded files are not reads), unzip uploads
                sp.run(['unzip', f'{MEDIA_ROOT}/{isolate.upload}.zip'])  # Assume client has given same filenames to contents as outer TODO Eliminate assumption
            sample = Sample(isolate=isolate, job=job)
            sample.save()

        # Make stages
        params = {}
        for i in range(first, last+1):
            for attr in STAGELIST[i]._meta.get_fields(include_parents=False):
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
    context['userEmail'] = Job.objects.get(id=kwargs['job_id']).user.email
    return render(request, 'foodbornePathogen/submitted.html', context)


def results(request, **kwargs):  # TODO Construct results page
    context = deepcopy(CONTEXT)
    context['userDir'] = f"{MEDIA_ROOT}{Job.objects.get(id=kwargs['job_id']).user.email}"
    context['jobID'] = kwargs['job_id']
    return render(request, 'foodbornePathogen/results.html', context)
