# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('user_messages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='groups',
            field=models.ManyToManyField(to='auth.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(verbose_name='Content'),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(related_name='sent_messages', verbose_name='Sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='sent_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Sent at'),
        ),
        migrations.AlterField(
            model_name='thread',
            name='subject',
            field=models.CharField(max_length=150, verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='thread',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Users', through='user_messages.UserThread', blank=True),
        ),
    ]
