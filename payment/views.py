from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import mixins

from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.session import check_stripe_session


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_object(self):
        payment_pk = self.kwargs["pk"]
        payment = get_object_or_404(Payment, pk=payment_pk)
        check_stripe_session(payment_pk)
        return payment
