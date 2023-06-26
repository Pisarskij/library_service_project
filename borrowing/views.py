from rest_framework import viewsets, mixins
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
