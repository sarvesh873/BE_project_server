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
