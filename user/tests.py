from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from user.models import User
from user.serializers import UserSerializer

USER_CRATE_URL = reverse("user:create-profile")
USER_PROFILE_URL = reverse("user:my-profile")


class CreateUserViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {
            "email": "test@test.com",
            "password": "password123",
            "first_name": "test",
            "last_name": "test",
        }

    def test_can_create_user(self):
        response = self.client.post(USER_CRATE_URL, self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@test.com")
        self.assertEqual(User.objects.get().first_name, "test")
        self.assertEqual(User.objects.get().last_name, "test")


class UserViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            password="password123",
            first_name="test",
            last_name="test",
        )
        self.client.force_authenticate(user=self.user)
        self.data = {
            "email": "test@test.com",
            "password": "password123",
            "first_name": "test1",
            "last_name": "test1",
        }

    def test_can_retrieve_user(self):
        response = self.client.get(USER_PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, UserSerializer(self.user).data)

    def test_can_update_my_profile(self):
        response = self.client.put(USER_PROFILE_URL, self.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, "test@test.com")
        self.assertEqual(self.user.first_name, "test1")
        self.assertEqual(self.user.last_name, "test1")
