import stripe
from django.db import transaction

from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import viewsets, mixins, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payment.models import Payment
from payment.session import create_stripe_session, get_days_difference
from .models import Borrowing
from .serializers import BorrowingListSerializer, BorrowingDetailSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get("user_id", None)
        is_active_str = self.request.query_params.get("is_active", None)
        """
        Return a queryset for the current user or user filtering by user_id in url
        ONLY for is_staff=true
        """
        if user.is_staff:
            queryset = (
                Borrowing.objects.filter(user_id=user_id)
                if user_id
                else Borrowing.objects.all()
            )
        # If is_staff=false will return only user-own borrowing
        else:
            queryset = Borrowing.objects.filter(user_id=user.id)
        """
        Return a queryset for is_active_str in url (is_active=True, return all datas with actual_return_date = null)
        ONLY for is_staff=false
        """
        if is_active_str is not None:
            is_active = is_active_str.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active)

        queryset = queryset.order_by("user_id")
        return queryset

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return BorrowingDetailSerializer
        return BorrowingListSerializer

    def perform_create(self, serializer):
        user = self.request.user
        validated_data = serializer.validated_data
        payment_borrowings = Borrowing.objects.filter(
            user_id_id=user.id,
        )
        book = validated_data["book_id"]

        if payment_borrowings.filter(
            borrowing_payments__status=Payment.PaymentStatusEnum.PENDING,
        ):
            raise serializers.ValidationError("User still not paid previous borrowing")

        if payment_borrowings.filter(
            actual_return_date__isnull=True,
        ):
            raise serializers.ValidationError("User already has an active borrowing")

        if book.inventory <= 0:
            raise serializers.ValidationError("This book is currently out of inventory")

        try:
            with transaction.atomic():
                data = validated_data["expected_return_date"]
                days_difference = get_days_difference(data=data)
                borrowing = serializer.save(user_id=self.request.user)
                create_stripe_session(
                    borrowing=borrowing,
                    days_difference=days_difference,
                    book=book,
                )
        except stripe.error.InvalidRequestError as e:
            raise serializers.ValidationError(e)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                type={"type": "int", "items": {"type": "number"}},
                description="Filter by user id (ex. ?user_id=2)",
            ),
            OpenApiParameter(
                "is_active",
                type={"type": "bool", "format": "bool"},
                description="Filter by is_active (ex. ?is_active=true)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
