from copy import deepcopy
from collections import namedtuple
from threading import Thread

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

from .models import *
from .forms import *

import subprocess
from subprocess import PIPE
import logging
logger = logging.getLogger("django")  # /projects/team-1/django/django.log

from django.http import HttpResponse

BASE_URL = "https://team1.predict2021.biosci.gatech.edu/"

temp = [f'{STAGES[first]}-{STAGES[last]}' for first, last in RANGES]
rc = zip(temp, RANGE_CHOICES)
CONTEXT = {'range_choices': rc}

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
    logger.debug("Full Python Subrocess Command: " + str(full_command))

    out = subprocess.run(full_command, shell=True, stdout=subprocess.DEVNULL)
    logger.debug("Subrocess Log: " + str(out))


def genome_assembly_pipeline(input_dir, output_dir, **options):
    logger.info("Genome Assembly Pipeline Selected")
    # Fill in code here Sara. - Matthew
    logger.info("Genome Assembly Pipeline Done...")

    
def gene_prediction_pipeline(input_dir, output_dir, **options):
    logger.info("Gene Prediction Pipeline Selected")
    command = '/projects/team-1/src/gene_prediction/src/fake_gene_prediction_master.py' \
        ' -i ' + input_dir + \
        ' -o ' + output_dir + \
        ' -t ' + str(options.get("threads"))
    run_bash_command_in_different_env(command, "gene_prediction")
    logger.info("Gene Prediction Pipeline Done...")

    
def functional_annotation_pipeline(input_dir, output_dir, **options):
    logger.info("Functional Annotation Pipeline Selected")
    # Fill in code here Sara. - Matthew
    logger.info("Functional Annotation Pipeline Done...")


def comparative_genomics_pipeline(input_dir, output_dir, **options):
    logger.info("Comparative Genomics Pipeline Selected")
    # Fill in code here Sara. - Matthew
    logger.info("Comparative Genomics Pipeline Done...")

    
def run_job(clientEmail, files, job, params):
    # clientemail - clientemail is the path.
    # files - basename (need full math from MEDIA_ROOT).
    # job - piepline stage tobe run (Class from models.py)
    # params - UI text box fields. print(params.items) to find out params.

    # If you want the fullpath - MEDIA_ROOT/clientemail/files

    logger.info('------------ run_job(clientEmail, files, job, params) -----------')
    logger.debug('clientEmail = ' + clientEmail)
    logger.debug('job.id = ' + str(job.id))
    logger.debug('job.pipeRange = ' + str(job.pipeRange))

    if job.pipeRange == 0:  # Full Pipeline
        genome_assembly_pipeline(
            input_dir = 'Unknown', \
            output_dir = 'Unknown')
        # Simply use the output of previous pipeline as input for next. - Matthew
        gene_prediction_pipeline(
            input_dir = 'projects/team-1/src/gene_prediction/data/input/', \ 
            output_dir = 'projects/team-1/src/gene_prediction/data/output/',\
            threads = 3)
        # Simply use the output of previous pipeline as input for next. - Matthew
        functional_annotation_pipeline(
            input_dir = 'Unknown', \
            output_dir = 'Unknown')
        # Simply use the output of previous pipeline as input for next. - Matthew
        comparative_genomics_pipeline(
            input_dir = 'Unknown', \
            output_dir = 'Unknown')
        
    elif job.pipeRange == 1:
        genome_assembly_pipeline(
            input_dir = 'Unknown', \
            output_dir = 'Unknown')
        
    elif job.pipeRange == 2:
        gene_prediction_pipeline(
            input_dir = 'projects/team-1/src/gene_prediction/data/input/', \
            output_dir = 'projects/team-1/src/gene_prediction/data/output/',\
            threads = 3)
        
    elif job.pipeRange == 3:
        functional_annotation_pipeline(
            input_dir = 'Unknown', \
            output_dir = 'Unknown')
        
    elif job.pipeRange == 4:
        comparative_genomics_pipeline(
            input_dir = 'Unknown', \
            output_dir = 'Unknown')
    # 5 GA - GP
    # 6 GA - FA
    # 7 GP - FA
    # 8 GP - CG
    # 9 FA - CG

    # Alternative is just to print out the link on results.
    # Contact user  TODO Figure out how to send email
    send_mail("Foodborn Pathogen job completed", MESSAGE.format(BASE_URL, job.id), from_email=None, recipient_list=[clientEmail])


def index(request):
    context = deepcopy(CONTEXT)
    return render(request, 'foodbornePathogen/index.html', context)


def terms(request):
    context = deepcopy(CONTEXT)
    return render(request, 'foodbornePathogen/terms.html', context)


def options(request, **kwargs):
    first, last = kwargs['range_choice'].split('-')
    first, last = int(STAGEINDS[first]), int(STAGEINDS[last])
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
        first, last = int(STAGEINDS[first]), int(STAGEINDS[last])
        pipeRange = RANGESINDS[(first, last)]
        job = Job(user=user, pipeRange=pipeRange)
        job.save()

        # Make isolates & samples
        for file in request.FILES.getlist('upload'):
            isolate = Isolate(user=user, upload=file)
            isolate.save()
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
        newJob = Thread(target=run_job, args=(userEmail, request.FILES.values(), job, params))
        newJob.start()

        return HttpResponseRedirect(f'/fbp/submitted/{job}')


def submitted(request, **kwargs):
    context = deepcopy(CONTEXT)
    context['userEmail'] = Job.objects.get(id=kwargs['job_id']).user.email
    return render(request, 'foodbornePathogen/submitted.html', context)


def results(request, **kwargs):  # TODO Construct results page
    context = deepcopy(CONTEXT)
    context['userDir'] = f"{MEDIA_ROOT}{Job.objects.get(id=kwargs['job_id']).user.email}"
    return render(request, 'foodbornePathogen/results.html', context)
