from datetime import timedelta, datetime, date

import stripe

from rest_framework import serializers

from book.models import Book
from library_service_project import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def get_current_timestamp():
    current_time = datetime.now()
    expires_at = current_time + timedelta(hours=23)
    return int(expires_at.timestamp())


def get_days_difference(data):
    today = date.today()
    days_difference = (data - today).days
    if days_difference < 1:
        raise serializers.ValidationError(
            "Expected return date must be in the future and minimum than 1 day"
        )
    return days_difference


def create_stripe_session(
    borrowing,
    book,
    days_difference,
    payment=None,
):
    expires_at_int = get_current_timestamp()
    daily_fee = book.daily_fee
    money_to_pay = int((daily_fee * 100) * days_difference)

    if payment is None:
        payment = Payment.objects.create(
            borrowing_id=borrowing,
            money_to_pay=money_to_pay,
        )

    session = stripe.checkout.Session.create(
        success_url=f"http://127.0.0.1:8000/api/payment/{borrowing.id}/",
        cancel_url=f"http://127.0.0.1:8000/api/payment/{borrowing.id}/",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Invoice for payment №{payment.id}",
                    },
                    "unit_amount": money_to_pay,
                },
                "quantity": 1,
            },
        ],
        expires_at=expires_at_int,
        mode="payment",
        metadata={"payment_id": payment.id},
    )

    payment.session_url = session.url
    payment.session_id = session.id
    payment.save()


def check_session_status(session_id=None):
    if session_id is not None:
        payment_session = stripe.checkout.Session.retrieve(session_id)
        status = payment_session.status
        return status
    return None


def check_stripe_data(payment_id):
    status = None
    payment = Payment.objects.get(id=payment_id)
    try:
        session_id = payment.session_id
        status = check_session_status(session_id)
    except stripe.error.InvalidRequestError as e:
        print(e)

    if status in ["open", "complete"]:
        return
    else:
        data = payment.borrowing_id.expected_return_date
        days_difference = get_days_difference(data=data)
        book = Book.objects.get(id=payment.borrowing_id.book_id.id)
        create_stripe_session(
            payment=payment,
            borrowing=payment.borrowing_id,
            book=book,
            days_difference=days_difference,
        )
