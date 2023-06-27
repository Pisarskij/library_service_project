from typing import Optional

from django.utils.functional import lazy
from rest_framework import viewsets, mixins, serializers

from rest_framework.permissions import IsAuthenticated
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
        """Set the user for the object"""
        book = serializer.validated_data["book_id"]
        if book.inventory <= 0:
            raise serializers.ValidationError("This book is currently out of inventory")
        serializer.save(user_id=self.request.user)
