from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "full_name", "phone","email","salary","goal")
    search_fields = ("username", "phone")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "returns")

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("user", "child_age", "child_edu_expi")