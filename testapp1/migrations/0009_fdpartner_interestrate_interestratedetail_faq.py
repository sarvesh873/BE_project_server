# Generated by Django 4.0.5 on 2024-03-07 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testapp1', '0008_fundurls'),
    ]

    operations = [
        migrations.CreateModel(
            name='FDPartner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partnerType', models.CharField(max_length=100, null=True)),
                ('institutionType', models.CharField(max_length=100, null=True)),
                ('heading', models.CharField(max_length=255, null=True)),
                ('logoUrl', models.URLField(null=True)),
                ('subHeading', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(null=True)),
                ('featuresHeading', models.CharField(max_length=255, null=True)),
                ('interestRatesRange', models.CharField(max_length=100, null=True)),
                ('minimumDeposit', models.CharField(max_length=100, null=True)),
                ('maximumDeposit', models.CharField(max_length=100, null=True)),
                ('lockIn', models.CharField(max_length=100, null=True)),
                ('tenure', models.CharField(max_length=100, null=True)),
                ('minimumInterestRate', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('maximumInterestRate', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('minimumInterestRateSeniorCitizens', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('maximumInterestRateSeniorCitizens', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('additionalInterestForSeniorCitizen', models.CharField(max_length=100, null=True)),
                ('etlink', models.URLField(null=True)),
                ('lastRevisedDate', models.DateField(null=True)),
                ('lastRevisedDateAbove2Cr', models.DateField(null=True)),
                ('partnerDetailsHTML', models.TextField(null=True)),
                ('metadataTitle', models.CharField(max_length=255, null=True)),
                ('metadataDescription', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InterestRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100)),
                ('categoryName', models.CharField(max_length=255)),
                ('fd_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interest_rates', to='testapp1.fdpartner')),
            ],
        ),
        migrations.CreateModel(
            name='InterestRateDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interestGeneralPublic', models.DecimalField(decimal_places=2, max_digits=5)),
                ('interestSeniorCitizen', models.DecimalField(decimal_places=2, max_digits=5)),
                ('tenure', models.CharField(max_length=100)),
                ('interest_rate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interest_rate_details', to='testapp1.interestrate')),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('conclusion', models.TextField(null=True)),
                ('fd_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faqs', to='testapp1.fdpartner')),
            ],
        ),
    ]