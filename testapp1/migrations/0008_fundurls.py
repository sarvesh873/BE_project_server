# Generated by Django 4.0.5 on 2024-02-28 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp1', '0007_child_child_name_alter_user_phone_family'),
    ]

    operations = [
        migrations.CreateModel(
            name='FundUrls',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
                ('url', models.URLField()),
            ],
        ),
    ]