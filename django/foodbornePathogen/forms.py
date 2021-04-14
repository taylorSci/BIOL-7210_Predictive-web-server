from django.forms import ModelForm
from django import forms

from .models import *


class GAStageForm(ModelForm):
    class Meta:
        model = GAStage
        exclude = ['job']


class GPStageForm(ModelForm):
    class Meta:
        model = GPStage
        exclude = ['job']


class FAStageForm(ModelForm):
    class Meta:
        model = FAStage
        exclude = ['job']


class CGStageForm(ModelForm):
    class Meta:
        model = CGStage
        exclude = ['job']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['email']


class UploadForm(ModelForm):
    class Meta:
        model = Isolate
        fields = ['upload']
        widgets = {'upload': forms.ClearableFileInput(attrs={'multiple': True})}