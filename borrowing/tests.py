from django.test import TestCase
from book.models import Book
from user.models import User
from borrowing.models import Borrowing
from datetime import datetime, timedelta


class BorrowingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="testuser@test.com", password="12345"
        )  # You might need to adjust this based on your User model
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverChoices.HARD,
            inventory=10,
            daily_fee=1.00,
        )

    def test_borrowing_creates(self):
        borrow = Borrowing.objects.create(
            expected_return_date=datetime.now() + timedelta(days=10),
            book_id=self.book,
            user_id=self.user,
        )
        self.assertEqual(
            self.book.inventory, 9
        )  # The book inventory should decrease by 1

    def test_borrowing_return(self):
        borrow = Borrowing.objects.create(
            expected_return_date=datetime.now() + timedelta(days=10),
            book_id=self.book,
            user_id=self.user,
        )
        borrow.actual_return_date = datetime.now()  # Return the book
        borrow.save()
        self.assertEqual(
            self.book.inventory, 10
        )  # The book inventory should increase by 1
