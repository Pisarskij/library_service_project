from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from user.models import User

BOOK_URL = "/api/books/"


class BookViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com",
            password="password123",
            first_name="test",
            last_name="test",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)
        self.data = {
            "title": "TestName",
            "author": "TestAuthor",
            "cover": "hard",
            "inventory": 1,
            "daily_fee": 10.0,
        }

    def test_can_create_book(self):
        response = self.client.post(BOOK_URL, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().title, "TestName")

    def test_increase_inventory(self):
        book = Book.objects.create(**self.data)
        book.increase_inventory()
        self.assertEqual(book.inventory, 2)  # inventory увеличился на 1

    def test_decrease_inventory(self):
        book = Book.objects.create(**self.data)
        book.decrease_inventory()
        self.assertEqual(book.inventory, 0)  # inventory уменьшился на 1

    def test_decrease_inventory_with_zero_inventory(self):
        book = Book.objects.create(**self.data)
        book.inventory = 0
        book.save()
        with self.assertRaises(ValueError):
            book.decrease_inventory()
