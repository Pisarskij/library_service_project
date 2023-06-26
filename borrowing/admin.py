from django.contrib import admin

from .models import Borrowing


class BorrowingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Borrowing, BorrowingAdmin)
