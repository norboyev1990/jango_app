# Generated by Django 3.0.7 on 2020-07-02 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0008_auto_20200702_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempdata',
            name='REGISTER_NUMBER',
            field=models.CharField(max_length=1000),
        ),
    ]