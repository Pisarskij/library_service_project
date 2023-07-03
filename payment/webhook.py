import stripe

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from library_service_project import settings
from payment.models import Payment

# The library needs to be configured with your account's secret key.
# Ensure the key is kept out of any version control system you might be using.
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

# This is your Stripe webhook secret for verifying the events.
endpoint_secret = settings.DJSTRIPE_WEBHOOK_SECRET


@csrf_exempt
@require_POST
def webhook(request):
    request = request
    payload = request.body
    sig_header = request.headers["Stripe-Signature"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return JsonResponse({"error": str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({"error": str(e)}, status=400)

    # Handle the event
    event_type = event["type"]
    if event_type == "checkout.session.completed":
        handle_payment_intent_succeeded(event)
    elif event_type == "payment_intent.payment_failed":
        handle_payment_intent_payment_failed(event)
    else:
        # Handle other event types
        print("Unhandled event type {}".format(event_type))

    return JsonResponse({"success": True})


def handle_payment_intent_succeeded(event):
    payment_intent = event["data"]["object"]
    instance_id = int(payment_intent["metadata"]["payment_id"])

    try:
        payment = Payment.objects.get(id=instance_id)
        payment.status = Payment.PaymentStatusEnum.PAID
        payment.save()
        print("Payment status updated to PAID:", instance_id)
    except Payment.DoesNotExist:
        print("Payment with ID {} does not exist".format(instance_id))


def handle_payment_intent_payment_failed(event):
    # TODO: Implement your logic for handling failed payment intents
    payment_intent = event["data"]["object"]
    print("Payment intent failed:", payment_intent["id"])
