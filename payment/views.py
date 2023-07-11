from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, serializers
from rest_framework import mixins
from rest_framework.response import Response

from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentListSerializer, PaymentDetailSerializer
from payment.session import check_stripe_data, create_stripe_session


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

    def perform_create(self, serializer):
        payment = serializer.save()
        return payment

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        borrowing_id = serializer.initial_data["borrowing_id"]
        borrowing = Borrowing.objects.get(id=borrowing_id)
        book = borrowing.book_id

        try:
            borrowing.borrowing_payments.get()
        except Payment.DoesNotExist:
            serializer.is_valid(raise_exception=True)
            test = self.perform_create(serializer)
            create_stripe_session(borrowing=borrowing, payment=test, book=book)
        else:
            raise serializers.ValidationError("Payment already exists")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
