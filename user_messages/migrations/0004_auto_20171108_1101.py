# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_messages', '0003_auto_20171108_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmemberthread',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='groupmemberthread',
            name='unread',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='userthread',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userthread',
            name='unread',
            field=models.BooleanField(default=True),
        ),
    ]
