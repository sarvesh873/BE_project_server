# Generated by Django 4.0.5 on 2024-03-07 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testapp1', '0014_faq_bulletpoints'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interestrate',
            name='fd_partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interestRates', to='testapp1.fdpartner'),
        ),
    ]
