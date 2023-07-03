import stripe

from drf_spectacular.utils import extend_schema, OpenApiParameter

from datetime import date

from rest_framework import viewsets, mixins, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from library_service_project import settings
from payment.models import Payment
from payment.session import create_stripe_session
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

        return queryset

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return BorrowingDetailSerializer
        return BorrowingListSerializer

    def perform_create(self, serializer):
        user = self.request.user

        # get Book.title
        book = serializer.validated_data["book_id"]

        # get Book.daily_fee
        daily_fee = serializer.validated_data["book_id"].daily_fee

        # get expected_return_date
        expected_return_date = serializer.validated_data["expected_return_date"]
        today = date.today()

        # get differences between expected_return_date and today
        days_difference = (expected_return_date - today).days
        if days_difference < 1:
            raise serializers.ValidationError(
                "Expected return date must be in the future and minimum than 1 day"
            )

        money_to_pay = int((daily_fee * 100) * days_difference)

        if book.inventory <= 0:
            raise serializers.ValidationError("This book is currently out of inventory")

            # Check if user already has an active borrowing
        active_borrowings = Borrowing.objects.filter(
            user_id=user.id, actual_return_date__isnull=True
        )
        if active_borrowings.exists():
            raise serializers.ValidationError("User already has an active borrowing")

        borrowing = serializer.save(user_id=self.request.user)

        payment_instance = Payment.objects.create(
            borrowing_id=borrowing,
            money_to_pay=money_to_pay,
        )

        # Create Payment with session_url and session_id
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        try:
            session = create_stripe_session(
                book=book,
                money_to_pay=money_to_pay,
                borrowing=borrowing.id,
                payment=payment_instance.id,
            )
        except stripe.error.InvalidRequestError:
            raise serializers.ValidationError(
                "Minimal amount to create payment link is: 0.5$"
            )

        # Save Payment with Borrowing and session details
        payment_instance.session_url = session.url
        payment_instance.session_id = session.id
        payment_instance.save()

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
