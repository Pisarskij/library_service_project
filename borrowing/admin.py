from django.contrib import admin
from .models import Borrowing


class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "book_id",
        "user_id",
    )
    search_fields = ("borrow_date", "book_id__title", "user_id__username")
    list_filter = ("borrow_date", "expected_return_date", "actual_return_date")


admin.site.register(Borrowing, BorrowingAdmin)
