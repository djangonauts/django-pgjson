# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pg_json_fields', '0002_textmodelwithdefault'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextModelWithIndent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('data', django_pgjson.fields.JsonField(options={'indent': 2})),
            ],
        ),
    ]
