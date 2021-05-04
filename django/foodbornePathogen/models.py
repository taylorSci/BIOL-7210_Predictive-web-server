import uuid
import os.path as osp

from django.db import models
from django.db.models import CASCADE
from django.conf import settings
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

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
RANGES_INDS = {e: i for i, e in enumerate(RANGES)}
STAGES = ['GA',
          'GP',
          'FA',
          'CG']
STAGE_INDS = {e: i for i, e in enumerate(STAGES)}
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

PARAMETER_ABBREVS = {'cut_mean_quality': 'M',
                     'average_qual': 'e',
                     'cut_window_size': 'W',
                     'kmer_size': 'k',
                     'min_block_size': 'b',
                     'block_coverage_threshold': 'c',

                     'run_GLIMMER': 'g',
                     'run_GeneMark': 'gm',
                     'run_Prodigal': 'p',

                     'clustering_identity': 'i',
                     'run_EggNOG': 'E',
                     'run_DeepARG': 'D',
                     'run_PilerCR': 'p',

                     'run_stringMLST': 'M',
                     'run_ANIm': 'm',
                     'run_parSNP': 'p',
                     'get_virulence_factors': 'V',
                     'get_resistance_factors': 'R'
                     }  # These map between parameters the user sees on the frontend, and options passed to the scripts on the backend


def getUserDir(instance, filename):
    base, _ = osp.splitext(filename)
    return f'{base}'


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

    def __str__(self):
        return str(self.upload)


class Job(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(to=User, on_delete=CASCADE)
    pipeRange = models.PositiveSmallIntegerField(choices=zip(range(len(RANGE_CHOICES)), RANGE_CHOICES))

    def __str__(self):
        return str(self.id)


min0valid = MinValueValidator(0, message="Minimum value of 0")
min1valid = MinValueValidator(0, message="Minimum value of 1")
max1valid = MaxValueValidator(1, message="Maximum value of 1")


# Because stage subtype forms are merged together to create an options webpage form, all attributes between subtypes must have distinct names.
class Stage(models.Model):
    job = models.ForeignKey(to=Job, on_delete=CASCADE)


class GAStage(Stage):
    # reconFlag = models.BooleanField(default=False)  # Tools not working that permit assembly reconciliation; SPAdes hardwired as assembler
    cut_mean_quality = models.PositiveSmallIntegerField(default=28, validators=[min0valid])  # FastP parameter
    average_qual = models.PositiveSmallIntegerField(default=28, validators=[min0valid])  # FastP parameter
    cut_window_size = models.PositiveSmallIntegerField(default=20, validators=[min1valid])  # FastP parameter
    # kmer_size = models.PositiveSmallIntegerField(default=21, validators=[min1valid])  # ABySS parameter
    # min_block_size = models.PositiveSmallIntegerField(default=10, validators=[min1valid])  # GAM-NGS parameter
    # block_coverage_threshold = models.FloatField(default=0.75, validators=[min0valid])  # GAM-NGS parameter


class GPStage(Stage):
    run_GLIMMER = models.BooleanField(default=False)  # At least 1 of GLIMMER, GeneMark, & Prodigal must run
    run_GeneMark = models.BooleanField(default=False)
    run_Prodigal = models.BooleanField(default=True)


class FAStage(Stage):
    clustering_identity = models.FloatField(default=0.95, validators=[min0valid, min1valid])
    # run_EggNOG = models.BooleanField(default=False)  # At least 1 of EggNOG, DeepARG, & PilerCR must run
    # run_DeepARG = models.BooleanField(default=True)
    run_PilerCR = models.BooleanField(default=False)


class CGStage(Stage):
    run_stringMLST = models.BooleanField(default=True)  # Requires FASTQ
    run_ANIm = models.BooleanField(default=True)  # Requires FASTA
    run_parSNP = models.BooleanField(default=False)  # Requires FASTA  # Heavier & more thorough than stringMLST
    get_virulence_factors = models.BooleanField(default=True)  # Requires FASTA
    get_resistance_factors = models.BooleanField(default=True)  # Requires _fa.gff from DeepARG


class Sample(models.Model):
    isolate = models.ForeignKey(to=Isolate, on_delete=CASCADE)
    job = models.ForeignKey(to=Job, on_delete=CASCADE)
