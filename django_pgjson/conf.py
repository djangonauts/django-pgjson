# -*- encoding: utf-8 -*-

from django.conf import settings

PGJSON_ENCODER_CLASS = getattr(settings, 'PGJSON_ENCODER_CLASS', 'django.core.serializers.json.DjangoJSONEncoder')
