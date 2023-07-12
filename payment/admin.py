from django.contrib import admin

from payment.models import Payment


class PaymentAdmin(admin.ModelAdmin):
    search_fields = ("status", "type", "borrowing_id__user__email")


admin.site.register(Payment, PaymentAdmin)
