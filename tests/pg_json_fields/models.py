# -*- coding: utf-8 -*-

from django.db import models
from django_pgjson.fields import JsonField


class TextModel(models.Model):
    data = JsonField()
