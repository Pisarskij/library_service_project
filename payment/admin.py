from django.contrib import admin

from payment.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    search_fields = ("status", "type", "borrowing_id__user__email")
    # list_filter = ("borrow_date", "expected_return_date", "actual_return_date")


admin.site.register(Payment, PaymentAdmin)
