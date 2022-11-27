from django.urls import path
from .views import *

urlpatterns =[
    path("users/", UserListAPIView.as_view(), name="users-list"),
    path("user/sign-up/", UserRegisterAPIView.as_view(), name="sign-up"),
    path("user/sign-in/", UserLoginAPIView.as_view(), name="sign-in"),
    path("user/verify-email/", VerifyEmail.as_view(), name="verify-email"),
    path("user/request-password-reset/", UserRequestPasswordResetAPI.as_view(), name="request-password-reset"),
    path("user/set-new-password/<uuidb64>/<token>/", SetNewPasswordAPI.as_view(), name="set-new-password"),
]