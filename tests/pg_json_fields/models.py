# -*- coding: utf-8 -*-

from django.db import models
from django_pgjson.fields import JsonField, JsonBField


class TextModel(models.Model):
    data = JsonField()

class TextModelB(models.Model):
    data = JsonBField()

class TextModelWithDefault(models.Model):
    data = JsonField(blank=True, default={})
