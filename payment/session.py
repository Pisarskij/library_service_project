import stripe
from django.http import JsonResponse

from borrowing.models import Borrowing
from library_service_project import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


def create_stripe_session(
    money_to_pay,
    payment=None,
    session=None,
):
    check_session = check_stripe_session(session)
    if not check_session or session is None:
        session = stripe.checkout.Session.create(
            success_url=f"http://127.0.0.1:8000/api/payment/{payment}/",
            cancel_url=f"http://127.0.0.1:8000/api/payment/{payment}/",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Invoice for payment №{payment}",
                        },
                        "unit_amount": money_to_pay,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            metadata={"payment_id": payment},
        )
        return session


def check_stripe_session(session_id):
    try:
        payment = stripe.PaymentIntent.retrieve(session_id)
        if payment.status == "succeeded":
            return JsonResponse({"valid": True})
        else:
            return JsonResponse({"valid": False})
    except stripe.error.InvalidRequestError:
        return JsonResponse({"valid": False})
