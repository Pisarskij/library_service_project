from django.db import models

from book.models import Book
from borrowing.models import Borrowing


class PaymentStatus(models.Choices):
    PENDING = "pending"
    PAID = "paid"


class PaymentType(models.Choices):
    PAYMENT = "payment"
    FINE = "fine"


class Payment(models.Model):
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    type = models.CharField(
        max_length=10,
        choices=PaymentType.choices,
        default=PaymentType.PAYMENT,
    )
    borrowing_id = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
