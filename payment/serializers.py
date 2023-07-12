from rest_framework import serializers

from payment.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing_id",
            "money_to_pay",
        ]
        read_only_fields = [
            "money_to_pay",
            "status",
            "type",
        ]


class PaymentDetailSerializer(PaymentListSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "type",
            "borrowing_id",
            "session_url",
            "session_id",
            "money_to_pay",
        ]
        read_only_fields = [
            "session_url",
            "session_id",
            "money_to_pay",
        ]
