# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-21 07:47
from __future__ import unicode_literals

import django.utils.timezone
import model_utils.fields
import positions.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nc_core', '0001_initial'),
        ('nc_clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(blank=True, max_length=512, verbose_name='title')),
                ('position', positions.fields.PositionField(default=0, verbose_name='position')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                              related_name='boards', to='nc_core.Company', verbose_name='company')),
            ],
            options={
                'verbose_name_plural': 'boards',
                'verbose_name': 'board',
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
                ('status',
                 models.CharField(choices=[('active', 'active'), ('archive', 'archive'), ('basket', 'basket')],
                                  default='active', max_length=32, verbose_name='status')),
                ('position', positions.fields.PositionField(default=0, verbose_name='position')),
                ('title', models.CharField(blank=True, default='', max_length=512, verbose_name='title')),
                ('color', models.CharField(blank=True, default='ffffff', max_length=16, verbose_name='color')),
                ('slug_id', models.PositiveIntegerField(default=0, verbose_name='slug id')),
                ('blocked', models.BooleanField(default=False, verbose_name='is blocked')),
                ('archive_date', models.DateTimeField(blank=True, null=True, verbose_name='archive at')),
                ('basket_date', models.DateTimeField(blank=True, null=True, verbose_name='to basket at')),
                ('blocked_by',
                 models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='blocked_cards', to=settings.AUTH_USER_MODEL,
                                   verbose_name='blocked by')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             to='nc_clients.Client', verbose_name='Client')),
            ],
            options={
                'verbose_name_plural': 'cards',
                'verbose_name': 'card',
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(blank=True, default='', max_length=512, verbose_name='title')),
                ('type', models.CharField(choices=[('regular', 'regular'), ('first', 'start workflow'), ('last', 'end workflow')], default='regular', max_length=32, verbose_name='type')),
                ('position', positions.fields.PositionField(default=-1, verbose_name='position')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='columns', to='nc_workflow.Board', verbose_name='board')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Users')),
            ],
            options={
                'verbose_name_plural': 'columns',
                'verbose_name': 'column',
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Subprocess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('column_from',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subprocess_from',
                                      to='nc_workflow.Column', verbose_name='source column')),
                ('column_to',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subprocess_to',
                                   to='nc_workflow.Column', verbose_name='destination column')),
            ],
            options={
                'verbose_name_plural': 'Subprocesses',
                'verbose_name': 'Subprocess',
            },
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('from_column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transitions_from', to='nc_workflow.Column', verbose_name='source column')),
                ('to_column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transitions_to', to='nc_workflow.Column', verbose_name='destination column')),
            ],
            options={
                'verbose_name_plural': 'transitions',
                'verbose_name': 'transition',
            },
        ),
        migrations.AddField(
            model_name='card',
            name='column',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='cards', to='nc_workflow.Column', verbose_name='column'),
        ),
        migrations.AddField(
            model_name='card',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='nc_core.Company', verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='card',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='card',
            name='user_created',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+',
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='card',
            name='user_modified',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='transition',
            unique_together=set([('from_column', 'to_column')]),
        ),
        migrations.AlterUniqueTogether(
            name='subprocess',
            unique_together=set([('column_to', 'column_from')]),
        ),
    ]
