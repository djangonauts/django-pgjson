# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pg_json_fields', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextModelWithDefault',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', django_pgjson.fields.JsonField(blank=True, default={})),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
