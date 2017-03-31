# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-30 13:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heartext', '0005_playlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='snippet',
            name='voice',
            field=models.CharField(choices=[(b'Joanna', b'Joanna (US)'), (b'Geraint', b'Geraint (Welsch)'), (b'Raveena', b'Raveena (Indian)'), (b'Kendra', b'Kendra (US'), (b'Amy', b'Amy (British)')], default=b'Joanna', max_length=40),
        ),
    ]