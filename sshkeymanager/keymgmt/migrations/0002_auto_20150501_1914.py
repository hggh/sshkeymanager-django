# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('keymgmt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sshaccount',
            name='name',
            field=models.CharField(validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(100), django.core.validators.RegexValidator(regex='^[0-9A-Za-z_.-]+$')], max_length=100, verbose_name='SSH Account Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sshaccountavailable',
            name='name',
            field=models.CharField(validators=[django.core.validators.MinLengthValidator(2), django.core.validators.MaxLengthValidator(100), django.core.validators.RegexValidator(regex='^[0-9A-Za-z_.-]+$')], max_length=100, unique=True, verbose_name='account name'),
            preserve_default=True,
        ),
    ]
