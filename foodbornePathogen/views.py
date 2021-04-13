from copy import deepcopy
from collections import namedtuple
from threading import Thread

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

from .models import *
from .forms import *

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


def run_job(clientEmail, files, job, params):
    # Run pipeline  TODO Call pipeline scripts
    pass

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
        for file in request.FILES.values():
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

        ### DIAGNOSTIC CODE  # TODO troubleshoot multiple file upload
        for k, v in request.POST.items():
            print(f"{k}: {v}")
        print('------------------')
        for i, e in enumerate(request.FILES.getlist('file_field')):
            print(f'{i}: {e}')
        print('------------------')
        for k, v in request.FILES.items():
            print(f"{k}: {v} ({type(v)})")
        ### DIAGNOSTIC CODE

        return HttpResponseRedirect(f'/fbp/submitted/{job}')


def submitted(request, **kwargs):
    context = deepcopy(CONTEXT)
    context['userEmail'] = Job.objects.get(id=kwargs['job_id']).user.email
    return render(request, 'foodbornePathogen/submitted.html', context)


def results(request, **kwargs):
    context = deepcopy(CONTEXT)
    context['userDir'] = f"{MEDIA_ROOT}{Job.objects.get(id=kwargs['job_id']).user.email}"
    return render(request, 'foodbornePathogen/results.html', context)
