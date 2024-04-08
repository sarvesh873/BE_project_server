# Generated by Django 4.0.5 on 2024-04-07 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testapp1', '0020_alter_password_host_key_alter_password_host_password_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NPSData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField()),
                ('name', models.CharField(max_length=100)),
                ('startinfo', models.CharField(max_length=100)),
                ('fund_size', models.CharField(max_length=20)),
                ('no_of_subs', models.CharField(max_length=20)),
                ('logo_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='NPSInterestRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=20)),
                ('code', models.CharField(max_length=10)),
                ('returns_5years', models.CharField(max_length=20)),
                ('nps_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='NPSinterestRates', to='testapp1.npsdata')),
            ],
        ),
    ]