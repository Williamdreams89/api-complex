from rest_framework import generics, views,status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
                        UserRegisterSerializer, 
                        VerifyEmailSerializer, 
                        UserRequestPasswordResetSerializer, 
                        SetNewPasswordSerializer,
                        UserLoginSerializer,
                        UserListSerializer
)
from .models import User
from .Utils import Utils
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import jwt
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, DjangoUnicodeDecodeError, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class UserRegisterAPIView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.validated_data
        serializer.save()
        user_email = serializer.data["email"]
        user = User.objects.get(email = user_email)
        username = user.full_name
        current_site = get_current_site(request).domain
        relative_path = reverse("verify-email")
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)
        absolute_url = "{}{}?token={}".format(current_site, relative_path, access_token)
        email_subject = "Verify your account"
        email_body = "Hello {}, \nPlease verify your account with the link below: \n{}".format(username,absolute_url)
        email_to = user.email
        data = {"email_subject":email_subject, "email_body": email_body, "email_to": email_to}
        success_message = "Verification link sent to email'{}'".format(user_email)
        Utils.send_email(data)
        return Response({
            "success": success_message,
            "email_body": email_body
        }, status=status.HTTP_200_OK)

class VerifyEmail(views.APIView):
    serializer_class = VerifyEmailSerializer
    token_param_config = openapi.Parameter("token", in_=openapi.IN_QUERY, description="Use your token", type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        try:
            token = request.GET.get("token")
            payload =  jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({"success": "Account verified successfully"}, status=status.HTTP_200_OK)
            return Response({"failed": "Account already verified !!"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError as identifier:
            return Response({"failed": "Expired token in email"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({"failed": "Invalid token in email"}, status=status.HTTP_400_BAD_REQUEST)

class UserRequestPasswordResetAPI(generics.GenericAPIView):
    serializer_class = UserRequestPasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        """Check whether the email from the request exist in the database
            or not; if exist: 
            1. Encode the user's id ==> uuidb66 with utils as url_base64_encode and smart_bytes
            2. Use PasswordResetTokenGenerator to make token for user 
            3. Send the token and the encoded id as reset link via email to user 
        """

        if User.objects.filter(email=request.data["email"]).exists():
            user = User.objects.get(email=request.data["email"])
            uuidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            print(f'{uuidb64=}')
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain
            relative_path = reverse("set-new-password", kwargs={"uuidb64": uuidb64, "token": token})
            absolute_url = "{}{}".format(current_site, relative_path)
            email_subject = "Reset your password"
            email_to = user.email
            email_body = "Hi, \n Use the link below to reset your password: \n {}".format(absolute_url)
            data = {"email_subject":email_subject, "email_body": email_body, "email_to": email_to}
            Utils.send_email(data)
            success_message = "Reset password link sent to {}".format(email_to)
            return Response({"success": success_message, "email_body": email_body}, status=status.HTTP_200_OK)
        return Response({"error": "User with this email not found"}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self, request, uuidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # uuidb64 = request.GET.get("uuidb64")
        # token = request.GET.get("reset-token")
        try: 
            """Force_str forces the encoded token to be converted to human readable or valid id """
            id = force_str(urlsafe_base64_decode(uuidb64))
            """Get user by the id above"""
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"failed": "Invalid password reset token"}, status=status.HTTP_401_UNAUTHORIZED)
            user.set_password(serializer.data["password"])
            user.save()
            return Response({"success": "Huraay password changed successfully"})

        except DjangoUnicodeDecodeError as identifier:
            return Response({"djangounicodeError": str(identifier)})
        # except Exception as e:
        #     return Response({"exception": str(e), "uuiddb": uuidb64, 'token': token})


class UserLoginAPIView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data

        user = User.objects.get(email=serializer.data["email"])

        refresh = RefreshToken.for_user(user)

        return Response({
            "success": "Logged in successfully !!!", 
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        }, status=status.HTTP_200_OK)




class UserListAPIView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.all()

    permission_classes =[
        permissions.IsAdminUser
    ]