from django_q.tasks import async_task
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, serializers

from rest_framework.permissions import IsAuthenticated

from .models import Borrowing
from .serializers import BorrowingListSerializer, BorrowingDetailSerializer
from .tasks import send_message


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
        """Set the user for the object"""
        book = serializer.validated_data["book_id"]
        if book.inventory <= 0:
            raise serializers.ValidationError("This book is currently out of inventory")
        borrowing = serializer.save(user_id=self.request.user)
        async_task(
            send_message,
            f"Borrowing №{borrowing.id} was created.\n"
            f"Book name: {book.title}\n"
            f"Borrowing date: {borrowing.borrow_date}\n"
            f"Return date: {borrowing.expected_return_date}\n"
            f"Daily fee: {book.daily_fee}$\n",
        )

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
