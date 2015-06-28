# -*- coding: utf-8 -*-

import json
import re
import django

import psycopg2
import psycopg2.extensions
import psycopg2.extras

from django import forms
from django.db import models
from django.db.backends.postgresql_psycopg2.version import get_version
from django.utils import six
from django.utils.module_loading import import_string

from .conf import settings


def get_encoder_class():
    return import_string(settings.PGJSON_ENCODER_CLASS)


class JsonAdapter(psycopg2.extras.Json):

    def __init__(self, *args, **kwargs):
        self.json_dump_args = kwargs.pop('json_dump_args', {})
        super(JsonAdapter, self).__init__(*args, **kwargs)

    def dumps(self, obj):
        return json.dumps(obj, cls=get_encoder_class(), **self.json_dump_args)


psycopg2.extensions.register_adapter(dict, JsonAdapter)
psycopg2.extras.register_default_json(loads=json.loads)

# so that psycopg2 knows also to convert jsonb fields correctly
# http://schinckel.net/2014/05/24/python,-postgres-and-jsonb/
psycopg2.extras.register_json(loads=json.loads, oid=3802, array_oid=3807)


class JsonField(six.with_metaclass(models.SubfieldBase, models.Field)):
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        self.json_dump_args = kwargs.pop('json_dump_args', {})
        super(JsonField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        if get_version(connection) < 90200:
            raise RuntimeError("django_pgjson does not supports postgresql version < 9.2")
        return "json"

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return json.dumps(self.get_prep_value(value), cls=get_encoder_class(),
                          **self.json_dump_args)

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default

        return None

    def to_python(self, value):
        if isinstance(value, six.string_types):
            try:
                value = json.loads(value)
            except ValueError:
                pass
        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': jsonFormField(self.json_dump_args)}
        defaults.update(kwargs)
        return super(JsonField, self).formfield(**defaults)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(JsonField, self).get_db_prep_value(value, connection, prepared=prepared)
        if self.null and value is None:
            return None
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


class JsonBField(JsonField):
    def db_type(self, connection):
        if get_version(connection) < 90400:
            raise RuntimeError("django_pgjson: PostgreSQL >= 9.4 is required for jsonb support.")
        return "jsonb"

    def get_prep_lookup(self, lookup_type, value, prepared=False):
        """ Cleanup value for the jsonb lookup types

        contains requires json encoded string
        has_any and has_all require array of string_types
        has requires string, but we can easily convert int to string

        """
        if lookup_type in ['jcontains']:
            if not isinstance(value, six.string_types):
                value = json.dumps(value, cls=get_encoder_class(),
                                   **self.json_dump_args)
        if lookup_type in ['jhas_any', 'jhas_all']:
            if isinstance(value, six.string_types):
                value = [value]
            # Quickly coerce the following:
            #   any iterable to array
            #   non-string values to strings
            value = ['%s' % v for v in value]
        elif lookup_type in ['jhas'] and not isinstance(value, six.string_types):
            if isinstance(value, six.integer_types):
                value = str(value)
            else:
                raise TypeError('jhas lookup requires str or int')
        return value

if django.get_version() >= '1.7':
    from .lookups import ExactLookup
    from .lookups import (ArrayLengthLookup, JsonBArrayLengthLookup, JsonBContainsLookup,
                          JsonBHasLookup, JsonBHasAnyLookup, JsonBHasAllLookup)

    JsonField.register_lookup(ExactLookup)
    JsonField.register_lookup(ArrayLengthLookup)

    JsonBField.register_lookup(ExactLookup)
    JsonBField.register_lookup(JsonBArrayLengthLookup)
    JsonBField.register_lookup(JsonBContainsLookup)
    JsonBField.register_lookup(JsonBHasLookup)
    JsonBField.register_lookup(JsonBHasAnyLookup)
    JsonBField.register_lookup(JsonBHasAllLookup)


def jsonFormField(json_dump_args_):
    class JsonFormField(forms.CharField):
        json_dump_args = json_dump_args_
        widget = forms.Textarea

        def prepare_value(self, value):
            if isinstance(value, six.string_types):
                return value
            return json.dumps(value, cls=get_encoder_class,
                              **self.json_dump_args)
    return JsonFormField


# South compatibility
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([(
        (JsonField,),
        [],
        {
            'blank': ['blank', {'default': True}],
            'null': ['null', {'default': True}],
        },
    )], (r'^django_pgjson\.fields\.JsonField',))

    add_introspection_rules([(
        (JsonBField,),
        [],
        {
            'blank': ['blank', {'default': True}],
            'null': ['null', {'default': True}],
        },
    )], (r'^django_pgjson\.fields\.JsonBField',))

except ImportError:
    pass
