from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from book.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book_id = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing",
    )
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrowing",
    )

    def __str__(self):
        return self.borrow_date


@receiver(pre_save, sender=Borrowing)
def manage_book_inventory(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        # This is a new borrowing, so decrease the book inventory.
        instance.book_id.decrease_inventory()
        return
    else:
        # This is an existing borrowing.
        # Check if the actual return date has been set.
        if not obj.actual_return_date and instance.actual_return_date:
            # The book was returned, so increase the book inventory.
            instance.book_id.increase_inventory()
            return
        instance.book_id.decrease_inventory()
