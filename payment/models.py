from enum import Enum

import stripe
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from enumfields import EnumIntegerField
from stripe.error import StripeError

from book.models import Book
from borrowing.models import Borrowing
from library_service_project import settings


class PaymentStatus(Enum):
    PENDING = 0
    PAID = 1


class PaymentType(Enum):
    PAYMENT = 0
    FINE = 1


class Payment(models.Model):
    status = EnumIntegerField(PaymentStatus, default=PaymentStatus.PENDING)
    type = EnumIntegerField(PaymentType, default=PaymentType.PAYMENT)
    borrowing_id = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(blank=True, null=True)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)


class StripeProduct(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    stripe_product_id = models.CharField(max_length=255, unique=True)


class StripePrice(models.Model):
    product = models.OneToOneField(StripeProduct, on_delete=models.CASCADE)
    stripe_price_id = models.CharField(max_length=255, unique=True)


@receiver(post_save, sender=Book)
def create_stripe_product_and_price(sender, instance, created, **kwargs):
    if created:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        product = stripe.Product.create(name=f"{instance.title}-{instance.id}")
        StripeProduct.objects.create(book=instance, stripe_product_id=product.id)

        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(instance.daily_fee * 100),  # Stripe uses cents
            currency="usd",
        )
        StripePrice.objects.create(product=product, stripe_price_id=price.id)


@receiver(post_save, sender=Payment)
def create_stripe_session(sender, instance, created, **kwargs):
    if created:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        book = instance.borrowing_id.book_id
        stripe_price = StripePrice.objects.get(product__book=book).stripe_price_id

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": stripe_price,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://127.0.0.1:8000/api/",
            cancel_url="https://127.0.0.1:8000/api/",
        )
        instance.session_url = session.url
        instance.session_id = session.id
        instance.save()


@receiver(pre_delete, sender=Book)
def delete_stripe_product_and_price(sender, instance, **kwargs):
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
    stripe_product = StripeProduct.objects.get(book=instance)
    stripe.Product.delete(stripe_product.stripe_product_id)
    stripe_product.delete()
