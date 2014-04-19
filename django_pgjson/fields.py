# -*- coding: utf-8 -*-

import json
import re
import django

from django.db.backends.postgresql_psycopg2.version import get_version
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django import forms
from django.utils import six

import psycopg2
import psycopg2.extensions
import psycopg2.extras


class JsonAdapter(psycopg2.extras.Json):
    def dumps(self, obj):
        return json.dumps(obj, cls=DjangoJSONEncoder)


psycopg2.extensions.register_adapter(dict, JsonAdapter)
psycopg2.extras.register_default_json(loads=json.loads)


class JsonField(six.with_metaclass(models.SubfieldBase, models.Field)):
    def db_type(self, connection):
        if get_version(connection) < 90200:
            raise RuntimeError("django_pgjson does not supports postgresql version < 9.2")
        return "json"

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return json.dumps(self.get_prep_value(value), cls=DjangoJSONEncoder)

    def to_python(self, value):
        if not isinstance(value, six.string_types):
            return value

        try:
            return json.loads(value)
        except ValueError:
            return value

    def formfield(self, **kwargs):
        defaults = {'form_class': JsonFormField}
        defaults.update(kwargs)
        return super(JsonField, self).formfield(**defaults)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(JsonField, self).get_db_prep_value(value, connection, prepared=prepared)
        return JsonAdapter(value)

    if django.get_version() >= '1.7':
        def get_transform(self, name):
            from .lookups import KeyTransformFactory

            transform = super(JsonField, self).get_transform(name)
            if transform:
                return transform

            if not re.match("at_\w+", name):
                return None

            _, key = name.split("_", 1)
            return KeyTransformFactory(key, self)


if django.get_version() >= '1.7':
    from .lookups import ExactLookup
    JsonField.register_lookup(ExactLookup)


class JsonFormField(forms.CharField):
    widget = forms.Textarea

    def prepare_value(self, value):
        if isinstance(value, six.string_types):
            return value
        return json.dumps(value, cls=DjangoJSONEncoder)


# South compatibility
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([(
        (JsonField,),
        [],
        {
            'blank': ['blank', { 'default': True }],
            'null': ['null', { 'default': True }],
        },
    )], (r'^django_pgjson\.fields\.JsonField',))
except ImportError:
    pass
