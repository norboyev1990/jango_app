# Generated by Django 3.0.7 on 2020-07-02 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0011_auto_20200702_1522'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportdata',
            old_name='NUMBER',
            new_name='NUMBERS',
        ),
    ]