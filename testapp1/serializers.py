from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import *
from datetime import datetime

class TokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token
    
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = [
            "username", 
            "first_name",
            "last_name",
            "password", 
            "email", 
            "phone", 
            ]

        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value
    def create(self, validated_data):
        email = validated_data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists.')
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['child_name', 'child_age', 'child_gender', 'child_edu_expi']
        extra_kwargs = {
            'child_name' : {'required' : True},
            'child_age': {'required': True},
            'child_gender': {'required': True},
            'child_edu_expi': {'required': True},
        }

class familySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ['family_name', 'family_age', 'family_gender', 'family_med_expi']
        extra_kwargs = {
            'family_name' : {'required' : True},
            'family_age': {'required': True},
            'family_gender': {'required': True},
            'family_med_expi': {'required': True},
        }

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(max_length=20, read_only=True)
    username = serializers.CharField(max_length=20,read_only=True)
    # is_admin = serializers.BooleanField(source='is_staff', read_only=True)
    # is_superuser = serializers.BooleanField(read_only=True)
    children = serializers.SerializerMethodField()
    family = serializers.SerializerMethodField()
    total_investment= serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "username", 
            "full_name",
            "email", 
            "phone", 
            # "is_admin",
            # "is_superuser",
            "salary",
            "goalAmount",
            "goalDuration",
            "location",
            "monthlyExpenditure",
            "age",
            "gender",
            "profession",
            "family_no_dep",
            "has_child",
            "num_children",
            "hasLoan",
            "laondura",
            "loanAmount",
            "hasInsurance",
            "insuranceAmount",
            "children",  # Include the child information in the serializer
            "family",
            "total_investment" 
        ]

    def get_children(self, obj):
        # Retrieve and serialize child data
        children_qs = Child.objects.filter(user=obj)
        children_serializer = ChildSerializer(children_qs, many=True)
        return children_serializer.data

    def get_family(self, obj):
        # Retrieve and serialize child data
        family_qs = Family.objects.filter(user=obj)
        family_serializer = familySerializer(family_qs, many=True)
        return family_serializer.data

    def validate_salary(self, value):
        if not value:
            # raise serializers.ValidationError("Error message")
            return 0
        return value
    
    def validate_goal(self, value):
        if not value:
            # raise serializers.ValidationError("goal != null")
            return 0
        return value
    
    def create(self, validated_data):
        children_data = validated_data.pop('children', [])
        family_data = validated_data.pop('family',[])
        user = super(ProfileSerializer, self).create(validated_data)

        for child_data in children_data:
            Child.objects.create(user=user, **child_data)
        
        for fami_data in family_data:
            Family.objects.create(user=user, **fami_data)

        return user

    def update(self, instance, validated_data):
        children_data = validated_data.pop('children', [])
        family_data = validated_data.pop('family',[])
        instance = super(ProfileSerializer, self).update(instance, validated_data)

        # Update or create child instances
        for child_data in children_data:
            child, created = Child.objects.update_or_create(user=instance, defaults=child_data)

        for fami_data in family_data:
            family, created = Family.objects.update_or_create(user=instance, defaults=fami_data)
        
        return instance
    
    def get_total_investment(self, obj):
        loan_emi = obj.loanAmount if obj.loanAmount else 0
        insuranceAmount= obj.insuranceAmount if obj.insuranceAmount else 0
        children_qs = Child.objects.filter(user=obj)
        child_edu_expi = sum(child.child_edu_expi for child in children_qs)
        family_qs = Family.objects.filter(user=obj)
        family_med_expi = sum(family.family_med_expi for family in family_qs)
        total_expenditure = loan_emi + child_edu_expi + family_med_expi + insuranceAmount + obj.monthlyExpenditure if obj.monthlyExpenditure else 0
        salary = obj.salary if obj.salary else 0
        total_investment = round(salary/12)-total_expenditure
        # print(total_investment,total_expenditure)
        return round(total_investment*0.4)


from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
             raise serializers.ValidationError({'detail': 'Token is expired or invalid'})
        

# class CompanyMatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = [
#             "id",
#             "name","returns"
#         ]

class MutualFundsMatchSerializer(serializers.Serializer):
    scheme_id = serializers.IntegerField()
    scheme_name = serializers.CharField()
    asSz = serializers.CharField()
    rtnDet_1 = serializers.CharField()
    rskRt = serializers.CharField()
    rtnRt = serializers.CharField()
    rt = serializers.CharField()
    lNv = serializers.CharField()
    sdWebUrl = serializers.CharField()
    logo = serializers.CharField()
    etmRnk = serializers.IntegerField()
    conRt = serializers.FloatField()
    expRat = serializers.FloatField()
    assetSizeFor = serializers.CharField()
    pCat = serializers.CharField()
    consistencyRating = serializers.CharField()
    rskratpoint = serializers.CharField()
    schemeAge = serializers.CharField()
    catDispName = serializers.CharField()
    performanceRank = serializers.DictField(child=serializers.IntegerField())
    returnpa = serializers.CharField() 


class MutualFundsListSerializer(serializers.Serializer):
    sId = serializers.IntegerField()
    oId = serializers.IntegerField()
    aId = serializers.IntegerField()
    name = serializers.CharField()
    amcName = serializers.CharField()
    lkn = serializers.BooleanField()
    lockinDays = serializers.IntegerField()
    isD = serializers.BooleanField()
    isBuyableV2 = serializers.BooleanField()
    isDiscoverable = serializers.BooleanField()
    nonDiscoverableReason = serializers.CharField()
    asSz = serializers.FloatField()
    rtnDet = serializers.DictField()
    rskRt = serializers.IntegerField()
    rtnRt = serializers.IntegerField()
    rt = serializers.IntegerField()
    lNv = serializers.FloatField()
    sdWebUrl = serializers.CharField()
    parName = serializers.CharField()
    etmCat = serializers.IntegerField()
    logo = serializers.URLField()
    etmRnk = serializers.IntegerField()
    conRt = serializers.IntegerField()
    expRat = serializers.FloatField()
    lDoDt = serializers.DictField()
    strtDt = serializers.DictField()
    catScCnt = serializers.IntegerField()
    dbldays = serializers.CharField()
    assetSizeFor = serializers.CharField()
    consistencyRating = serializers.IntegerField()
    rskratpoint = serializers.ListField(child=serializers.CharField())
    schemeAge = serializers.CharField()
    pCatURL = serializers.CharField()
    pCat = serializers.CharField()
    catURL = serializers.CharField()
    catDispName = serializers.CharField()
    etmRankDispTheme = serializers.CharField()
    expRatStr = serializers.CharField()
    defultDuration = serializers.IntegerField()
    performanceRanking = serializers.DictField()

class FixedDepositSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    partnerType = serializers.CharField()
    institutionType = serializers.CharField()
    heading = serializers.CharField()
    logoUrl = serializers.URLField()
    subHeading = serializers.CharField()
    description = serializers.CharField()
    featuresHeading = serializers.CharField()
    interestRatesRange = serializers.CharField()
    minimumDeposit = serializers.CharField()
    maximumDeposit = serializers.CharField()
    lockIn = serializers.CharField()
    tenure = serializers.CharField()
    minimumInterestRate = serializers.FloatField()
    maximumInterestRate = serializers.FloatField()
    minimumInterestRateSeniorCitizens = serializers.FloatField()
    maximumInterestRateSeniorCitizens = serializers.FloatField()
    additionalInterestForSeniorCitizen = serializers.CharField()
    etlink = serializers.URLField()
    lastRevisedDate = serializers.CharField()
    lastRevisedDateAbove2Cr = serializers.CharField()
    partnerDetailsHTML = serializers.CharField()
    metadataTitle = serializers.CharField()
    metadataDescription = serializers.CharField()

    class Meta:
        model = FDPartner
        fields = '__all__'

class InterestRateDetailSerializer(serializers.Serializer):
    interestGeneralPublic = serializers.FloatField()
    interestSeniorCitizen = serializers.FloatField()
    tenure = serializers.CharField()
    class Meta:
        model = InterestRateDetail
        fields = ['interestGeneralPublic', 'interestSeniorCitizen', 'tenure']

class InterestRateSerializer(serializers.Serializer):
    category = serializers.CharField()
    categoryName = serializers.CharField()
    interestRatesList = InterestRateDetailSerializer(many=True)
    class Meta:
        model = InterestRate
        fields = ['category', 'categoryName', 'interestRatesList']

class FAQSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    bulletPoints = serializers.ListField(child=serializers.CharField(), required=False)
    class Meta:
        model = FAQ
        fields = ['title', 'description', 'bulletPoints']

class FDPartnerSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    partnerType = serializers.CharField()
    institutionType = serializers.CharField()
    heading = serializers.CharField()
    logoUrl = serializers.URLField()
    subHeading = serializers.CharField()
    description = serializers.CharField(allow_null=True,required=False)
    featuresHeading = serializers.CharField()
    interestRatesRange = serializers.CharField()
    minimumDeposit = serializers.CharField()
    maximumDeposit = serializers.CharField()
    lockIn = serializers.CharField()
    tenure = serializers.CharField()
    minimumInterestRate = serializers.FloatField()
    maximumInterestRate = serializers.FloatField()
    minimumInterestRateSeniorCitizens = serializers.FloatField()
    maximumInterestRateSeniorCitizens = serializers.FloatField()
    additionalInterestForSeniorCitizen = serializers.CharField()
    etlink = serializers.URLField()
    interestRates = InterestRateSerializer(many=True)
    lastRevisedDate = serializers.DateField()
    lastRevisedDateAbove2Cr = serializers.DateField()
    partnerDetailsHTML = serializers.CharField()
    faqs = FAQSerializer(many=True)
    metadataTitle = serializers.CharField()
    metadataDescription = serializers.CharField()

    def create(self, validated_data):
        interest_rates_data = validated_data.pop('interestRates')
        faqs_data = validated_data.pop('faqs')

        fd_partner = FDPartner.objects.create(**validated_data)

        for interest_rate_data in interest_rates_data:
            interest_rate_details_data = interest_rate_data.pop('interestRatesList')
            interest_rate = InterestRate.objects.create(fd_partner=fd_partner, **interest_rate_data)
            for detail_data in interest_rate_details_data:
                InterestRateDetail.objects.create(interest_rate=interest_rate, **detail_data)

        for faq_data in faqs_data:
            FAQ.objects.create(fd_partner=fd_partner, **faq_data)

        return fd_partner
    
    def to_internal_value(self, data):
        if 'lastRevisedDate' in data:
            data['lastRevisedDate'] = datetime.strptime(data['lastRevisedDate'], '%d %b %Y').strftime('%Y-%m-%d')
        if 'lastRevisedDateAbove2Cr' in data:
            data['lastRevisedDateAbove2Cr'] = datetime.strptime(data['lastRevisedDateAbove2Cr'], '%d %b %Y').strftime('%Y-%m-%d')
        return super().to_internal_value(data)
    
    class Meta:
        model = FDPartner
        fields = ['partnerType', 'institutionType', 'heading', 'logoUrl', 'subHeading', 'description', 'featuresHeading', 'interestRatesRange', 'minimumDeposit', 'maximumDeposit', 'lockIn', 'tenure', 'minimumInterestRate', 'maximumInterestRate', 'minimumInterestRateSeniorCitizens', 'maximumInterestRateSeniorCitizens', 'additionalInterestForSeniorCitizen', 'etlink', 'lastRevisedDate', 'lastRevisedDateAbove2Cr', 'partnerDetailsHTML', 'metadataTitle', 'metadataDescription', 'interestRates', 'faqs']


class NPSInterestRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPSInterestRate
        fields = ['category', 'code', 'returns_5years']

class NPSSerializer(serializers.ModelSerializer):
    NPSinterestRates = NPSInterestRateSerializer(many=True)

    class Meta:
        model = NPSData
        fields = ['id', 'link', 'name', 'startinfo', 'fund_size', 'NPSinterestRates', 'no_of_subs', 'logo_url']

    def create(self, validated_data):
        interest_rates_data = validated_data.pop('NPSinterestRates')
        nps_data = NPSData.objects.create(**validated_data)
        for rate_data in interest_rates_data:
            NPSInterestRate.objects.create(nps_data=nps_data, **rate_data)
        return nps_data
    


class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ['first_name', 'email', 'subject', 'description']