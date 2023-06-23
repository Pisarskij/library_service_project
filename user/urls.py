from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import CreateUserView, UserView, SelfUserProfileView

app_name = "user"

router = routers.DefaultRouter()
router.register("profile", UserView, basename="profile")

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create_profile"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("profile/me/", SelfUserProfileView.as_view(), name="my_profile"),
    path("", include(router.urls)),
]
