# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import keymgmt.validators
import re
import django.core.validators
import model_utils.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='environment name', max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(100), django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+$', 32), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('updated', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Group Name', max_length=32, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(32), django.core.validators.RegexValidator(message='Only A-Za-z0-9\\s_-. are allowed!', regex='^[0-9A-Za-z\\s_.-]+$')])),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('updated', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='GroupRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('rule', models.CharField(verbose_name='Group Rule', max_length=32, validators=[keymgmt.validators.validate_regex])),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('updated', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated')),
                ('group', models.ForeignKey(to='keymgmt.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Host Name', max_length=155, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(155), django.core.validators.RegexValidator(message='Hostname is not valid.', regex='^[0-9A-Za-z_.-]+$')])),
                ('ipaddress', models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('updated', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated')),
                ('environment', models.ForeignKey(to='keymgmt.Environment')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SSHAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='SSH Account Name', max_length=100, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(100), django.core.validators.RegexValidator(regex='^[0-9A-Za-z_.-]+$')])),
                ('obj_name', models.CharField(verbose_name='Object Name', max_length=100, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.RegexValidator(regex='^(environment|host|group)$')])),
                ('obj_id', models.IntegerField(verbose_name='Object Id')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SSHAccountAvailable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='account name', max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(100), django.core.validators.RegexValidator(regex='^[0-9A-Za-z_.-]+$')])),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SSHKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='SSH Key Name', max_length=32, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(32), django.core.validators.RegexValidator(message='Only A-Za-z0-9\\s_-. are allowed!', regex='^[0-9A-Za-z\\s_.-]+$')])),
                ('sshkey', models.TextField(verbose_name='SSH Key', validators=[keymgmt.validators.validate_sshkey])),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('updated', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SSHKeyring',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='SSH Keyring', max_length=32, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(32), django.core.validators.RegexValidator(message='Only A-Za-z0-9\\s_-. are allowed!', regex='^[0-9A-Za-z\\s_.-]+$')])),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('updated', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated')),
                ('keys', models.ManyToManyField(to='keymgmt.SSHKey')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='sshaccount',
            name='keyrings',
            field=models.ManyToManyField(to='keymgmt.SSHKeyring'),
        ),
        migrations.AddField(
            model_name='sshaccount',
            name='keys',
            field=models.ManyToManyField(to='keymgmt.SSHKey'),
        ),
        migrations.AddField(
            model_name='group',
            name='hosts',
            field=models.ManyToManyField(to='keymgmt.Host'),
        ),
        migrations.AlterUniqueTogether(
            name='sshaccount',
            unique_together=set([('name', 'obj_name', 'obj_id')]),
        ),
    ]
