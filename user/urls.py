from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views import CreateUserView, SelfUserProfileView

app_name = "user"

urlpatterns = [
    path("", CreateUserView.as_view(), name="create-profile"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", SelfUserProfileView.as_view(), name="my-profile"),
]
