# -*- encoding: utf-8 -*-

from appconf import AppConf
from django.conf import settings  # noqa - do not remove


class PGJSONConf(AppConf):

    class Meta:
        holder = 'django.conf.settings'
        prefix = 'pgjson'
        proxy = True

    ENCODER_CLASS = 'django.core.serializers.json.DjangoJSONEncoder'
