from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from user.models import User
from user.serializers import UserSerializer, UserCreateSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    authentication_classes = ()
    permission_classes = ()


class SelfUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    queryset = User.objects

    def get_object(self):
        return self.request.user
