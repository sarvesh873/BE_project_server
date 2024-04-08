from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.safestring import mark_safe
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ParseError
from rest_framework.views import APIView
from .serializers import *
from .models import *
import hashlib, json
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
import requests
from django.contrib.auth.tokens import default_token_generator
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from cryptography.fernet import Fernet


PASSWORD_RESET_URL = (
    "http://127.0.0.1:8000//forget-password/{token}/{uid}"
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        token_pair = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(token_pair, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    serializer_class = TokenPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class PasswordResetView(generics.GenericAPIView):


    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)
            reset_url = mark_safe(PASSWORD_RESET_URL.format(token=token, uid=uid))
            context = {"user": user, "reset_url": reset_url}
            html_message = render_to_string("password-reset.html", context=context)
            send_mail(
                'Reset your password',
                '',
                settings.EMAIL_HOST_USER,
                [email],
                html_message=html_message,
                fail_silently=False,)

            return Response(
                {"message": "Link sent to mail!"}, status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            raise ValidationError({"email": "This email dosn't belongs to any user"})


class PasswordResetConfirmView(generics.GenericAPIView):
    def post(self, request):
        uid = request.data["uid"]
        user_id = urlsafe_base64_decode(uid)
        token = request.data["token"]
        new_password = request.data["new_password"]
        user = User.objects.get(id=user_id)
        if not user:
            message = "User doesn't exist"
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
        elif default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "password reset success"}, status=status.HTTP_200_OK
            )
        else:
            message = "Link is invalid or expired"
        return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


# salary , goal  
class ProfileView(generics.RetrieveAPIView,generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


    def get_object(self):
        return self.request.user
    
    # To update users goal and salary
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,data=request.data,partial=True)
        if (serializer.is_valid()):
            children_data = request.data.get('children', [])
            family_data = request.data.get('family',[])
            serializer.save()  # Save the user instance first

            # Update or create child instances
            Child.objects.filter(user=instance).delete()  # Delete existing children
            for child_data in children_data:
                Child.objects.create(user=instance, **child_data)
            
            Family.objects.filter(user=instance).delete()  # Delete existing Family
            for fami_data in family_data:
                Family.objects.create(user=instance, **fami_data)
            # print(serializer.data)
            return super().update(request, *args, **kwargs)
        
        return Response({"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


# MutualFundsMatching to user data    
class MutualFundsMatch(generics.GenericAPIView):
    serializer_class = MutualFundsMatchSerializer
    permission_classes = [IsAuthenticated]
    # function to convert the input duration into days as per our api requirement
    def convert_to_days(input_string):
        parts = input_string.lower().split()
        duration = int(parts[0])
        unit = parts[1]

        if unit == "month" or unit == "months":
            days = str(duration * 30)
        elif unit == "year" or unit == "years":
            days = str(duration * 365)
        else:
            raise ValueError("Invalid unit. Please use 'months' or 'years'.")

        return days

    def post(self, request):
        # Get data from the request
        input_returns = request.data.get('input_returns')
        input_duration = request.data.get('input_duration')
        input_days = MutualFundsMatch.convert_to_days(input_duration)
        input_amt = request.data.get('input_amt')
        goal = self.request.user.goal
        input_risk = request.data.get('input_risk')
        input_cat = request.data.get('input_cat')

        url = FundUrls.objects.get(name='mutualfundmatch').url

        response = requests.get(url)
        if response.status_code == 200:
            # Extract JSON data from the response
            data = response.json()
            # List to store selected entries
            selected_entries = []
            # Iterate over the schemes in the JSON data
            for scheme in data["mfSchemeMiniList"]:
                scheme_id = scheme["sId"]
                scheme_data = data["mfSchemeCalculatorReturnMap"].get(str(scheme_id))
                
                # Check if scheme data exists and if SIP returns for 365 days meets the condition
                if scheme_data:
                    sip_returns = scheme_data[input_returns].get(input_days)
                    if sip_returns: # Check if SIP returns 
                            if not input_risk or input_risk in scheme["rskratpoint"]:
                                # If input_cat is not provided or if the scheme category matches input_cat
                                if not input_cat or scheme["pCat"] == input_cat:
                                    # Calculate expected return for expected year SIP
                                    expected_return = sip_returns * (input_amt / 1000)  # SIP amount / 1000
                                    if expected_return >= goal:  
                                        xirr_value = scheme_data["xirrDurationWise"].get(input_days, 0) 
                                        # print(xirr_value)
                                        selected_entries.append({
                                            "scheme_id": scheme_id,
                                            "scheme_name": scheme["name"],
                                            "asSz": scheme["asSz"],
                                            "rtnDet_1": scheme["rtnDet"].get("1", 0),
                                            "rskRt": scheme["rskRt"],
                                            "rtnRt": scheme["rtnRt"],
                                            "rt": scheme["rt"],
                                            "lNv": scheme["lNv"],
                                            "sdWebUrl": "https://www.etmoney.com/"+scheme["sdWebUrl"],
                                            "logo": scheme["logo"],
                                            "etmRnk": scheme["etmRnk"],
                                            "conRt": scheme["conRt"],
                                            "expRat": scheme["expRat"],
                                            "pCat":scheme["pCat"],
                                            "assetSizeFor": scheme["assetSizeFor"].replace("&#8377;", "₹ "),
                                            "consistencyRating": scheme["consistencyRating"],
                                            "rskratpoint": scheme["rskratpoint"],
                                            "schemeAge": scheme["schemeAge"],
                                            "catDispName": scheme["catDispName"],
                                            "performanceRank": {
                                                "rank": scheme["performanceRanking"]["rank"],
                                                "rankOutOf": scheme["performanceRanking"]["rankOutOf"]
                                            },
                                            "returnpa":"{:.2f}%".format(xirr_value * 100)
                                        })
                                        selected_entries.sort(key=lambda x: x["returnpa"], reverse=True)
            serializer = MutualFundsMatchSerializer(selected_entries, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("Failed to retrieve data", status=response.status_code)
        

# All available MutualFundsList
class MutualFundsList(generics.ListAPIView):
    serializer_class = MutualFundsListSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        d_url = FundUrls.objects.get(name='mutualfundlist').url

        size = self.request.query_params.get('size', 20)  # Default size is 20
        url = f"{d_url}?size={size}"

        response = requests.get(url)
        # Total funds are 1139 ,funds with hybrid category are 171 ,funds with debt category are 387,funds with EQUITY category are 555  
        # COMMODITIES(GOLD INVESTMENT) 22 ,OTHERS 4(issue with the data of this scheme)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            pCat = self.request.query_params.get('pCat')

            # If pCat is provided, filter based on pCat
            if pCat:
                filtered_funds = [fund for fund in data.get("mfSchemeMiniList", []) if fund.get('pCat') == pCat]
                return filtered_funds
            else:
                # Return all funds if pCat is not provided the list of companies from the JSON data
                return data.get("mfSchemeMiniList", [])

        else:
            return Response("Failed to retrieve data", status=response.status_code)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# All available Fixed Deposits
class FixedDepositList(generics.ListAPIView):
    queryset = FDPartner.objects.all()  # Retrieve all objects from FDPartner model
    # we have 16 fdpartners with all of the data
    serializer_class = FixedDepositSerializer 

# to create new Fixed Deposit
class FDPartnerCreateAPIView(APIView):
    serializer_class = FDPartnerSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data.get('fdPartnerDetails', []), many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = {"error": str(e)}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


# Fixed Deposits to user data   
class FixedDepositMatch(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FDPartnerSerializer

    #function to check if the users duration is withun the fund tenure  
    def is_within_tenure(input_duration: str, tenure: str) -> bool:
        # Extract lower and upper bounds from the tenure string
        tenure_values = [int(value.split()[0]) for value in tenure.split(' - ')]
        # If tenure is specified in days, convert it to years
        if 'yr' not in tenure:
            tenure_values = [value / 365 for value in tenure_values]
        # Extract numerical value and units from input duration
        input_value, input_unit = input_duration.split()
        # Convert input duration to months if specified in years
        if input_unit == 'yrs':
            input_value = int(input_value) * 12
        elif input_unit == 'months':
            input_value = int(input_value)
        # Check if the input value falls within the range
        if len(tenure_values) == 1:  # Only one value provided (no upper bound)
            return int(input_value) == int(tenure_values[0] * 12)
        else:
            return int(tenure_values[0] * 12) <= int(input_value) <= int(tenure_values[1] * 12)
    # Example usage: input_duration = "1 yrs" tenure = "365 - 449" print(is_within_tenure(input_duration, tenure))  # Output: True input_duration = "5 yrs" tenure = "1 yr - 10 yrs" print(is_within_tenure(input_duration, tenure))  # Output: True input_duration = "46 months" tenure = "1096 - 1679" print(is_within_tenure(input_duration, tenure))  # Output: True

    def post(self, request):
        try:
            data = request.data
            input_duration = data.get('input_duration')
            input_amt = data.get('input_amt')
            goal = self.request.user.goal
            user_age = self.request.user.age

            selected_entries_fd = []
            unique_ids = set()
            # Filter FDPartner objects based on specific criteria if needed
            schemes = FDPartner.objects.all()

            for scheme in schemes:
                if(FixedDepositMatch.is_within_tenure(input_duration, scheme.tenure)):
                    for interest_rate_data in scheme.interestRates.all():
                        if (goal > 20000000 and interest_rate_data.category == 'CATEGORY_2') or interest_rate_data.category == 'CATEGORY_1':
                            for rate in interest_rate_data.interestRatesList.all():
                                if(FixedDepositMatch.is_within_tenure(input_duration, rate.tenure)):
                                    if user_age > 60:
                                        interest_rate = rate.interestSeniorCitizen
                                    else:
                                        interest_rate = rate.interestGeneralPublic
                                
                                    irate = interest_rate / 100
                                    years = int(input_duration.split()[0])
                                    # Calculate the exponential term
                                    exponential_term = (1 + irate) ** years
                                    
                                    # Calculate the initial amount needed
                                    initial_amount_needed = goal / exponential_term
                                    
                                    # Round off the initial amount to the nearest integer
                                    rounded_initial_amount = round(initial_amount_needed)
                                    # Check if the ID is unique, if so, add it to the list
                                    if scheme.id not in unique_ids:
                                        selected_entries_fd.append({
                                            "id": scheme.id,
                                            "partnerType": scheme.partnerType,
                                            "institutionType": scheme.institutionType,
                                            "heading": scheme.heading,
                                            "logoUrl": scheme.logoUrl,
                                            "subHeading": scheme.subHeading,
                                            "desired_investment_amount":rounded_initial_amount,
                                            "intrest_rate":interest_rate,
                                            "tenure":rate.tenure
                                        })
                                    unique_ids.add(scheme.id)
            selected_entries_fd.sort(key=lambda x: x['desired_investment_amount'])
            return Response(selected_entries_fd)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


# Sukanya Samriddhi Yojana (SSY)
class SSYdetail(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            data = request.data
            tinv = int(data.get("total_investment"))
            ssyi = 8.2
            user = self.request.user
            eligible_child = False
            for child in user.child_set.all():
                if child.child_age < 10 and child.child_gender == 'Female':
                    eligible_child = True
                    break

            if eligible_child:
                rinv = tinv
                totali = 0
                for i in range(15):
                    totali = (((rinv / 100) * ssyi) + rinv)
                    rinv = totali + tinv

                for i in range(15, 21):
                    totali = (((totali / 100) * ssyi) + totali)

                xtinv = (tinv * 15)
                xtint = totali - (tinv * 15)
                xmval = totali

                result = {
                    "Total Investment": xtinv,
                    "Total Interest": round(xtint),
                    "Maturity Value": round(xmval),
                     "Scheme Link": "https://www.nsiindia.gov.in/(S(icaeepnc0emp2n55wzmnrz55))/InternalPage.aspx?Id_Pk=89"
                }
            else:
                result = {"message": "You are not eligible for this scheme"}

            return Response(result)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

# Public Provident Fund (PPF)
class PPFdetail(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            data = request.data
            tinv = int(data.get("total_investment"))
            tdura = int(data.get("total_duration"))
            # Rate of interest is set by the government, every quarter. 7.1% is the current interest rate considered for calculating returns.
            ppfi = 7.1 
            user = self.request.user

            if user.age>18 and tdura>14:
                rinv = tinv
                totali = 0
                for i in range(tdura):
                    totali = (((rinv / 100) * ppfi) + rinv)
                    rinv = totali + tinv


                xtinv = (tinv * tdura)
                xtint = totali - (tinv * tdura)
                xmval = totali

                result = {
                    "Total Investment": xtinv,
                    "Total Interest": round(xtint),
                    "Maturity Value": round(xmval),
                     "Scheme Link": "https://www.nsiindia.gov.in/(S(2ideic21latgdcbrimbchqqo))/InternalPage.aspx?Id_Pk=55"
                }
            else:
                result = {"message": "You are not eligible for this scheme"}

            return Response(result)

        except Exception as e:
            return Response({"error": str(e)}, status=500)       
        
# NPS 
class NPSCreateAPIView(generics.CreateAPIView):
    serializer_class = NPSSerializer
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = {"error": str(e)}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

class NPSMatch(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            goal = float(request.user.goal)
            user_age = request.user.age
            tenure = 60 - user_age
            category = request.data.get('category')  

            nps_funds = NPSData.objects.all()
            investment_details = []
            for fund in nps_funds:
                interest_rates = fund.NPSinterestRates.all()
                for rate in interest_rates:
                    if rate.category == category:
                        interest_rate = float(rate.returns_5years.split('%')[0]) / 100
                        code = rate.code

                        r = interest_rate / 12
                        n = tenure * 12
                        monthly_investment = (goal * r) / (pow(1 + r, n) - 1)
                        
                        investment_details.append({
                            'fund_name': fund.name,
                             'link': fund.link,
                            'startinfo': fund.startinfo,
                            'fund_size': fund.fund_size,
                            'no_of_subs': fund.no_of_subs,
                            'logo_url': fund.logo_url,
                            'code': code,
                            'interest_rate':round(interest_rate*100,2),
                            'monthly_investment_amount': round(monthly_investment, 2)
                        })
                        break  # Stop iterating through interest rates once found

            return Response(investment_details)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)