# -*- coding: utf-8 -*-
from django.forms.models import ModelForm
from .models import IntModel


class IntArrayForm(ModelForm):
    class Meta:
        model = IntModel
