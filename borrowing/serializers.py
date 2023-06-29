from rest_framework import serializers

from book.serializers import BookSerializer
from payment.serializers import PaymentSerializer
from .models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    payments = serializers.SlugRelatedField(many=True, read_only=True, slug_field="id")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id",
            "payments",
        ]
        read_only_fields = [
            "id",
            "user_id",
        ]


class BorrowingDetailSerializer(BorrowingListSerializer):
    book_id = BookSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id",
            "payments",
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book_id",
            "user_id",
        ]
