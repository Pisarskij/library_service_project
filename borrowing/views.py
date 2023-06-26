from rest_framework import viewsets, mixins, serializers
from .models import Borrowing
from .serializers import BorrowingListSerializer, BorrowingDetailSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()

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
