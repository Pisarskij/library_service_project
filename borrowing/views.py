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
        if user.is_staff:
            return Borrowing.objects.all()
        return Borrowing.objects.filter(user_id=user.id)

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
