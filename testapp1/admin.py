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
    list_display = ("user","child_name", "child_age","child_gender", "child_edu_expi")


@admin.register(Family)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("user","family_name", "family_age","family_gender", "family_med_expi")

@admin.register(FundUrls)
class UrlsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url")
