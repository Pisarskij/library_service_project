from django.db import models

from book.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()  # TODO: add options
    actual_return_date = models.DateField()  # TODO: add options
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing",
    )
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrowing",
    )
