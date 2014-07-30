# -*- coding: utf-8 -*-

from django.utils.functional import cached_property
from django.utils import six
from django.db.models import Transform, Lookup


class KeyTransform(Transform):
    def __init__(self, key, base_field, *args, **kwargs):
        super(KeyTransform, self).__init__(*args, **kwargs)
        try:
            self.key = int(key)
        except ValueError:
            self.key = key

        self.base_field = base_field

    def as_sql(self, qn, connection):
        lhs, params = qn.compile(self.lhs)

        if isinstance(self.key, int):
            return "%s->>%s" % (lhs, self.key), params

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


class ExactLookup(Lookup):
    lookup_name = 'exact'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)

        if len(rhs_params) == 1 and hasattr(rhs_params[0], "adapted"):
            adapted = rhs_params[0].adapted
            if isinstance(adapted, six.string_types):
                rhs_params[0] = adapted

        params = lhs_params + rhs_params
        return '%s = %s' % (lhs, rhs), params


class ArrayLengthLookup(Lookup):
    lookup_name = 'array_length'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'json_array_length(%s) = %s' % (lhs, rhs), params


class JsonBArrayLengthLookup(Lookup):
    lookup_name = 'array_length'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'jsonb_array_length(%s) = %s' % (lhs, rhs), params


class JsonBContainsLookup(Lookup):
    """
    jsonb-specific containment lookup that can be used as follows::

        YourModel.objects.filter(data__jcontains={"author": "John Smith"}

    This will be translated into the following SQL::

        select * from yourmodel where data @> '{"author": "John Smith"}'::jsonb

    You can also do interesting queries like::

        MyMovie.objects.filter(data__jcontains={"tags": ["sad", "romantic"]}

    Such queries can be accelerated by GiN indices on the jsonb field in
    question.

    :author: Charl P. Botha <cpbotha@vxlabs.com>

    """

    # ideally we would call this 'contains'. However, in Django 'contains'
    # lookups are explicitly handled by LIKE queries, and the
    # Field.get_db_prep_lookup will then prepare your data for a DB LIKE query
    # breaking our jsonb containment query. -- cpb
    lookup_name = 'jcontains'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "{0} @> {1}::jsonb".format(lhs, rhs), params
