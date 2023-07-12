from rest_framework import viewsets, mixins

from user.permissions import IsAdminOrIfAnonReadOnly
from .models import Book
from .serializers import BookSerializer


class BookViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAnonReadOnly,)
