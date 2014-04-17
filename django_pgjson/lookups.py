# -*- coding: utf-8 -*-

from django.utils.functional import cached_property
from django.db.models import Transform


class KeyTransform(Transform):
    def __init__(self, key, base_field, *args, **kwargs):
        super(KeyTransform, self).__init__(*args, **kwargs)
        self.key = key
        self.base_field = base_field

    def as_sql(self, qn, connection):
        lhs, params = qn.compile(self.lhs)
        import pdb; pdb.set_trace()

        return "%s->>'%s'" % (lhs, self.key), params

    @cached_property
    def output_type(self):
        return self.base_field


class KeyTransformFactory(object):
    def __init__(self, key, base_field):
        self.key = key
        self.base_field = base_field

    def __call__(self, *args, **kwargs):
        return KeyTransform(self.key, self.base_field, *args, **kwargs)

