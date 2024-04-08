from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    # user related paths
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path("refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    # password reset
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
     path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #  mutual funds related paths
    path('mutual-funds-match/', MutualFundsMatch.as_view(), name="mutual_funds_match"),
     path('all-mf-listing/', MutualFundsList.as_view(), name="mutual_funds_list"),
    #  fixed deposit related paths
    path('fixed_deposit-match/', FixedDepositMatch.as_view(), name="fixed_deposit_match"),
     path('all-fd-listing/', FixedDepositList.as_view(), name='fixed_deposit_list'),
     path('create-fd-partner/', FDPartnerCreateAPIView.as_view(), name='create_fd_partner'),
    #  Sukanya Samriddhi Yojana (SSY) related paths
    path('ssy/', SSYdetail.as_view(),name="sukanya_samriddhi_yojana" ),
    # Public Provident Fund (PPF) related paths
    path('ppf/', PPFdetail.as_view(),name="public_provident_fund" ),
    # Nps 
    path('create-nps/', NPSCreateAPIView.as_view(), name='nps-data'),
    path('nps-match/', NPSMatch.as_view(), name='nps_match'),
]