from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length = 10, null = True)
    salary = models.IntegerField(null=True)
    goal = models.IntegerField(null=True)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length = 10, choices = GENDER_CHOICES, null=True)
    profession = models.CharField(max_length = 12, null = True)
    family_no_dep = models.IntegerField(null = True)

    # New fields for child information
    has_child = models.BooleanField(default=False)
    num_children = models.IntegerField(default=0)


    # New fields for loan details
    has_loan = models.BooleanField(default=False)
    loan_duration = models.IntegerField(null=True)
    loan_emi = models.IntegerField(null=True)



    @property
    def full_name(self):
        name = "%s %s" % (self.first_name, self.last_name)
        return name.strip()

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.username) + " pk: " + str(self.pk)


class Child(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=20, null=True)
    child_age = models.IntegerField(null=True)
    child_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    child_edu_expi = models.IntegerField(null=True)


class Family(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    family_name = models.CharField(max_length=20, null=True)
    family_age = models.IntegerField(null=True)
    family_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    family_med_expi = models.IntegerField(null=True)

# company => id,name,returns(int),
class Company(models.Model):
    name = models.CharField(max_length=15)
    returns = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.name}"

class FundUrls(models.Model):
    name = models.CharField(max_length=15)
    url = models.URLField() 

    def __str__(self) -> str:
        return f"{self.name}"


class FDPartner(models.Model):
    id=models.IntegerField(primary_key=True)
    partnerType = models.CharField(max_length=100, null=True)
    institutionType = models.CharField(max_length=100, null=True)
    heading = models.CharField(max_length=255, null=True)
    logoUrl = models.URLField(null=True)
    subHeading = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    featuresHeading = models.CharField(max_length=255, null=True)
    interestRatesRange = models.CharField(max_length=100, null=True)
    minimumDeposit = models.CharField(max_length=100, null=True)
    maximumDeposit = models.CharField(max_length=100, null=True)
    lockIn = models.CharField(max_length=100, null=True)
    tenure = models.CharField(max_length=100, null=True)
    minimumInterestRate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    maximumInterestRate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    minimumInterestRateSeniorCitizens = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    maximumInterestRateSeniorCitizens = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    additionalInterestForSeniorCitizen = models.CharField(max_length=100, null=True)
    etlink = models.URLField(null=True)
    lastRevisedDate = models.CharField(max_length=100,null=True)
    lastRevisedDateAbove2Cr = models.CharField(max_length=100,null=True)
    partnerDetailsHTML = models.TextField(null=True)
    metadataTitle = models.CharField(max_length=255, null=True)
    metadataDescription = models.CharField(max_length=255, null=True)

class InterestRate(models.Model):
    category = models.CharField(max_length=100)
    categoryName = models.CharField(max_length=255)
    fd_partner = models.ForeignKey(FDPartner, related_name='interestRates', on_delete=models.CASCADE)

class InterestRateDetail(models.Model):
    interestGeneralPublic = models.DecimalField(max_digits=5, decimal_places=2)
    interestSeniorCitizen = models.DecimalField(max_digits=5, decimal_places=2)
    tenure = models.CharField(max_length=100)
    interest_rate = models.ForeignKey(InterestRate, related_name='interestRatesList', on_delete=models.CASCADE)


class FAQ(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    bulletPoints = models.TextField(null=True) 
    fd_partner = models.ForeignKey(FDPartner, related_name='faqs', on_delete=models.CASCADE)



class Password(models.Model):
    HOST_USER = models.BinaryField(max_length=555)
    HOST_PASSWORD = models.BinaryField(max_length=555)
    HOST_KEY = models.BinaryField(max_length=555, null=True)


class NPSData(models.Model):
    link = models.URLField()
    name = models.CharField(max_length=100)
    startinfo = models.CharField(max_length=100)
    fund_size = models.CharField(max_length=20)
    no_of_subs = models.CharField(max_length=20)
    logo_url = models.URLField()

class NPSInterestRate(models.Model):
    nps_data = models.ForeignKey(NPSData, related_name='NPSinterestRates', on_delete=models.CASCADE)
    category = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    returns_5years = models.CharField(max_length=20)