# -*- encoding: utf-8 -*-

import uuid

from django.core.serializers.json import DjangoJSONEncoder


class CustomJSONEncoder(DjangoJSONEncoder):

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return obj.hex
        return super(CustomJSONEncoder, self).default(obj)
