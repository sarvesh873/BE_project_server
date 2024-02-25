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
import hashlib
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum

from rest_framework_simplejwt.authentication import JWTAuthentication



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

# class PasswordResetView(generics.GenericAPIView):
#     def post(self, request):
#         email = request.data.get("email")

#         try:
#             user = User.objects.get(email=email)
#             uid = urlsafe_base64_encode(force_bytes(user.id))
#             token = default_token_generator.make_token(user)
#             reset_url = mark_safe(PASSWORD_RESET_URL.format(token=token, uid=uid))
#             context = {"user": user, "reset_url": reset_url}
#             html_message = render_to_string("password-reset.html", context=context)
#             send_mail(
#                 'Reset your password',
#                 '',
#                 settings.EMAIL_HOST_USER,
#                 [email],
#                 html_message=html_message,
#                 fail_silently=False,)

#             return Response(
#                 {"message": "Link sent to mail!"}, status=status.HTTP_200_OK
#             )

#         except User.DoesNotExist:
#             raise ValidationError({"email": "This email dosn't belongs to any user"})


# class PasswordResetConfirmView(generics.GenericAPIView):
#     def post(self, request):
#         uid = request.data["uid"]
#         user_id = urlsafe_base64_decode(uid)
#         token = request.data["token"]
#         new_password = request.data["new_password"]
#         user = User.objects.get(id=user_id)
#         if not user:
#             message = "User doesn't exist"
#             return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)
#         elif default_token_generator.check_token(user, token):
#             user.set_password(new_password)
#             user.save()
#             return Response(
#                 {"message": "password reset success"}, status=status.HTTP_200_OK
#             )
#         else:
#             message = "Link is invalid or expired"
#         return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


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
    

class CompanyList(generics.ListAPIView):
    serializer_class = CompanyMatchSerializer
    queryset = Company.objects.all()
    permission_classes = [IsAuthenticated]
    
    
class CompanyMatch(generics.ListAPIView):
    serializer_class = CompanyMatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        goal = self.request.user.goal
        return Company.objects.filter(returns__gte=goal)

    
    