# Generated by Django 4.0.5 on 2024-04-20 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp1', '0021_npsdata_npsinterestrate'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='goaldura',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='has_insurance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='insurance_emi',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.CharField(max_length=12, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='monthly_expi',
            field=models.IntegerField(null=True),
        ),
    ]
