import stripe
from rest_framework import viewsets, status
from rest_framework.response import Response

from library_service_project import settings
from payment.models import Payment
from payment.serializers import PaymentSerializer
from rest_framework import mixins

from book.models import Book


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        borrowing_id = request.data["borrowing_id"]
        money_to_pay = request.data["money_to_pay"]

        book = Book.objects.get(
            id=borrowing_id
        )  # Получаем экземпляр Book по идентификатору

        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
        session = stripe.checkout.Session.create(
            success_url="https://127.0.0.1/success",
            cancel_url="https://127.0.0.1/cancel",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": book.title,  # Используем название экземпляра Book
                        },
                        "unit_amount": int(
                            money_to_pay * 100
                        ),  # Сумма платежа в центах
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
        )

        payment = Payment.objects.create(
            borrowing_id=borrowing_id,
            money_to_pay=money_to_pay,
            session_url=session.url,
            session_id=session.id,
        )

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
