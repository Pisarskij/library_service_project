from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import mixins

from payment.models import Payment
from payment.serializers import PaymentListSerializer, PaymentDetailSerializer
from payment.session import check_stripe_data


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentListSerializer

    def get_object(self):
        payment_pk = self.kwargs["pk"]
        check_stripe_data(payment_pk)
        payment = get_object_or_404(Payment, pk=payment_pk)
        return payment
