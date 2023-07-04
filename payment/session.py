from _decimal import Decimal
from datetime import timedelta, datetime

import stripe

from library_service_project import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def create_stripe_session(
    borrowing,
    book,
    days_difference,
    session=None,
):
    check_session = check_stripe_session(session)
    if not check_session or session is None:
        daily_fee = book.daily_fee
        money_to_pay = int((daily_fee * 100) * days_difference)

        # Get the current time
        current_time = datetime.now()

        # Calculate the expiration time as 23 hours, 59 minutes, and 59 seconds from the current time
        expires_at = current_time + timedelta(hours=23, minutes=59, seconds=59)

        # Convert the expiration time to an integer timestamp
        expires_at_int = int(expires_at.timestamp())

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
        return session


def check_stripe_session(payment_id=None):
    if payment_id is not None:
        try:
            payment = Payment.objects.get(id=payment_id)
            session_id = payment.session_id
            payment_session = stripe.checkout.Session.retrieve(session_id)
            status = payment_session.status

            if status == "open":
                return True
            else:
                pass
                # check_actual_stripe_session_link(payment=payment)
        except stripe.error.InvalidRequestError as e:
            print(e)
            return True
