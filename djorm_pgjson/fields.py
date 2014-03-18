# -*- coding: utf-8 -*-

import json
import re

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.backends.postgresql_psycopg2.version import get_version
from django import forms
from django.utils import six


class JSONField(six.with_metaclass(models.SubfieldBase, models.Field)):
    rx_int = re.compile(r'^[\d]+$')
    rx_float = re.compile(r'^([\d]+\.[\d]*|\.[\d]+)$')

    def __init__(self, null=True, blank=True, default={}, *args, **kwargs):
        super(JSONField, self).__init__(*args, null=null, blank=blank,
                                        default=default, **kwargs)

    def db_type(self, connection):
        return 'json' if connection.vendor == 'postgresql' and get_version(connection) >= 90200 else 'text'

    def get_prep_value(self, value):
        return json.dumps(value, cls=DjangoJSONEncoder)

    def to_python(self, value):
        if not isinstance(value, six.string_types):
            return value

        if self.rx_int.match(value):
            return int(value)

        if self.rx_float.match(value):
            return float(value)

        if value in ('true', 'false', 'null'):
            return json.loads(value)

        if value.startswith(('{','[','"')) and value.endswith(('}',']','"')):
            return json.loads(value)

        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': JSONFormField}
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([(
        (JSONField,),
        [],
        {
            'blank': ['blank', { 'default': True }],
            'default': ['default', { 'default': '{}' }],
            'null': ['null', { 'default': True }],
        },
    )], (r'^djorm_pgjson\.fields\.JSONField',))
except ImportError:
    pass


class JSONFormField(forms.CharField):
    widget = forms.Textarea

    def prepare_value(self, value):
        return json.dumps(value, cls=DjangoJSONEncoder)
