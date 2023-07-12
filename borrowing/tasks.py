import os

from _decimal import Decimal

from aiogram import Bot

from asgiref.sync import async_to_sync

from django.utils import timezone
from django_q.tasks import async_task

from borrowing.models import Borrowing
from payment.models import Payment

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))


async def async_send_message(text: str):
    await bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=text)


def send_message(text: str):
    async_to_sync(async_send_message)(text)


def check_borrowing_overdue():
    now = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        actual_return_date=None, expected_return_date__lt=now
    )
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            payments = Payment.objects.get(borrowing_id=borrowing.id)
            money_to_pay = Decimal(payments.money_to_pay / 100)

            text = (
                f"User: {borrowing.user_id.email}\n"
                f"You borrowing №{borrowing.id} is overdue!"
                f"\nExpected return date: {borrowing.expected_return_date}"
                f"\nTo paid: {money_to_pay}$"
            )
            async_task(send_message, text)
    else:
        text = "No borrowings overdue today!"
        async_task(send_message, text)
