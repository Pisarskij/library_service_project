from django.db import models
from django_enum import EnumField

from book.models import Book
from borrowing.models import Borrowing


class Payment(models.Model):
    class PaymentStatusEnum(models.IntegerChoices):
        PENDING = 0, "pending"
        PAID = 1, "paid"

    class PaymentTypeEnum(models.IntegerChoices):
        PAYMENT = 1, "payment"
        FINE = 0, "fine"

    status = EnumField(PaymentStatusEnum, null=True, blank=True, default=0)
    type = EnumField(
        PaymentTypeEnum,
        null=True,
        blank=True,
    )
    borrowing_id = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments", default=0
    )
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.status
