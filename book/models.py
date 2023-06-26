from django.db import models


class Book(models.Model):
    class CoverChoices(models.Choices):
        HARD = "hard"
        SOFT = "soft"

    title = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=155)
    cover = models.CharField(
        max_length=10,
        choices=CoverChoices.choices,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

    def decrease_inventory(
        self,
    ):
        if self.inventory > 0:
            self.inventory -= 1
            self.save()
        else:
            raise ValueError("Inventory cannot be negative")

    def increase_inventory(
        self,
    ):
        self.inventory += 1
        self.save()
