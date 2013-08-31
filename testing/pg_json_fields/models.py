# -*- coding: utf-8 -*-

from django.db import models
from djorm_pgjson.fields import JSONField
from djorm_expressions.models import ExpressionManager


class TextModel(models.Model):
    data = JSONField()
    objects = ExpressionManager()
