# serializers.py
from rest_framework import serializers

from book.serializers import BookSerializer
from .models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id",
        ]
        read_only_fields = [
            "id",
            "user_id",
        ]


class BorrowingDetailSerializer(BorrowingListSerializer):
    book_id = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id",
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book_id",
            "user_id",
        ]
