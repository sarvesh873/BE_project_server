from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import *

class TokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
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
            "goal",
            "age",
            "gender",
            "profession",
            "family_no_dep",
            "has_child",
            "num_children",
            "has_loan",
            "loan_duration",
            "loan_emi",
            "children",  # Include the child information in the serializer
            "family"
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
        

class CompanyMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name","returns"
        ]