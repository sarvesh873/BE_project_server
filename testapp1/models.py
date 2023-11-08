from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length = 12, null = True)

    @property
    def full_name(self):
        name = "%s %s" % (self.first_name, self.last_name)
        return name.strip()

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.username) + " pk: " + str(self.pk)
