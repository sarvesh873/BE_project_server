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


@admin.register(FDPartner)
class FDdataAdmin(admin.ModelAdmin):
    list_display = ("id", "partnerType", "heading")

@admin.register(InterestRate)
class FDdataAdmin(admin.ModelAdmin):
    list_display = ("category", "categoryName", "fd_partner")

@admin.register(InterestRateDetail)
class FDdataAdmin(admin.ModelAdmin):
    list_display = ("interestGeneralPublic", "interestSeniorCitizen", "tenure","interest_rate")

@admin.register(FAQ)
class FDdataAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "bulletPoints","fd_partner")

@admin.register(Password)
class PasswordAdmin(admin.ModelAdmin):
    list_display = ("HOST_USER","HOST_PASSWORD","HOST_KEY")

class NPSInterestRateInline(admin.TabularInline):
    model = NPSInterestRate
    
class NPSDataAdmin(admin.ModelAdmin):
    inlines = [NPSInterestRateInline]
admin.site.register(NPSData, NPSDataAdmin)