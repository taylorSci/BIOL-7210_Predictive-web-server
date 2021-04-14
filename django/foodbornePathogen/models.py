import uuid

from django.db import models
from django.db.models import CASCADE
from django.conf import settings
from django import forms

MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

RANGES = [(0, 3),
          (0, 0),
          (1, 1),
          (2, 2),
          (3, 3),
          (0, 1),
          (0, 2),
          (1, 2),
          (1, 3),
          (2, 3)]
RANGESINDS = {e: i for i, e in enumerate(RANGES)}
STAGES = ['GA',
          'GP',
          'FA',
          'CG']
STAGEINDS = {e: i for i, e in enumerate(STAGES)}
RANGE_CHOICES = ['Full Pipeline',
                 'Genome Assembly',
                 'Gene Prediction',
                 'Functional Annotation',
                 'Comparative Genomics',
                 'GA - GP',
                 'GA - FA',
                 'GP - FA',
                 'GP - CG',
                 'FA - CG']


def getUserDir(instance, filename):
    return f'{instance.user.email}/{filename}'


class User(models.Model):
    email = models.EmailField(max_length=70, blank=True, unique=True)

    def __str__(self):
        return self.email


class Isolate(models.Model):
    user = models.ForeignKey(to=User, on_delete=CASCADE)
    upload = models.FileField(upload_to=getUserDir)
    seqReadsAvailable = models.BooleanField(default=False)
    assembliesAvailable = models.BooleanField(default=False)
    genesAvailable = models.BooleanField(default=False)
    annotationsAvailable = models.BooleanField(default=False)
    analysesAvailable = models.BooleanField(default=False)

    def __str__(self):
        return str(self.upload)


class Job(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(to=User, on_delete=CASCADE)
    pipeRange = models.PositiveSmallIntegerField(choices=zip(range(len(RANGE_CHOICES)), RANGE_CHOICES))

    def __str__(self):
        return str(self.id)


# Because stage subtype forms are merged together to create an options webpage form, all attributes between subtypes must have distinct names.
class Stage(models.Model):
    job = models.ForeignKey(to=Job, on_delete=CASCADE)


class GAStage(Stage):
    reconFlag = models.BooleanField(default=False)
    cut_mean_quality = models.PositiveSmallIntegerField(default=28)  # FastP parameter
    average_qual = models.PositiveSmallIntegerField(default=28)  # FastP parameter
    cut_window_size = models.PositiveSmallIntegerField(default=20)  # FastP parameter
    kmer_size = models.PositiveSmallIntegerField(default=21)  # ABySS parameter
    min_block_size = models.PositiveSmallIntegerField(default=10)  # GAM-NGS parameter
    block_coverage_threshold = models.FloatField(default=0.75)  # GAM-NGS parameter


class GPStage(Stage):
    pass  # TODO Write stage parameters


class FAStage(Stage):
    pass  # TODO Write stage parameters


class CGStage(Stage):
    pass  # TODO Write stage parameters


class Sample(models.Model):
    isolate = models.ForeignKey(to=Isolate, on_delete=CASCADE)
    job = models.ForeignKey(to=Job, on_delete=CASCADE)
