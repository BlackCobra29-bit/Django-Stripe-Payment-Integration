import logging
import stripe
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import tutorials, Purchaser

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def tutorial_list(request):
    tutorials_list = tutorials.objects.all()
    context = {"tutorials": tutorials_list}
    return render(request, "tutorial_list.html", context)


@login_required
def stripe_checkout(request, tutorial_id):
    try:
        get_tutorial = get_object_or_404(tutorials, pk=tutorial_id)

        if get_tutorial.price <= 0:
            logger.error(f"Invalid price for tutorial {tutorial_id}.")
            return redirect('tutorial_list')  # Redirect or handle the error accordingly

        tutorial_price_in_cent = int(get_tutorial.price * 100)

        stripe_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": tutorial_price_in_cent,
                    "product_data": {"name": get_tutorial.title},
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("payment-success")),
            cancel_url=request.build_absolute_uri(reverse("payment-cancel")),
            metadata={"tutorial_id": get_tutorial.id, "buyer_id": request.user.id},
        )

        return redirect(stripe_session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return redirect('tutorial_list')  # Redirect or handle the error appropriately


@csrf_exempt
@require_POST
def webhook_manager(request):
    stripe_payload = request.body.decode('utf-8')
    signature_header = request.META.get("HTTP_STRIPE_SIGNATURE", None)
    if not signature_header:
        return JsonResponse({"error": "Missing signature"}, status=400)

    try:
        stripe_event = stripe.Webhook.construct_event(
            stripe_payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signatures"}, status=400)

    if stripe_event["type"] == "checkout.session.completed":
        stripe_session = stripe_event["data"]["object"]
        logger.info("Checkout Session Completed!")
        manage_checkout_session(stripe_session)

    return JsonResponse({"status": "success"})


def manage_checkout_session(stripe_session):
    tutorial_id = stripe_session["metadata"]["tutorial_id"]
    user_id = stripe_session["metadata"]["buyer_id"]

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found.")
        return

    tutorial = get_object_or_404(tutorials, pk=tutorial_id)
    purchaser = Purchaser.objects.create(user=user)
    purchaser.purchased_courses.set([tutorial])


@login_required
def payment_success(request):

    return render(request, "payment_success.html")


@login_required
def payment_cancel(request):
    
    return render(request, "payment_cancel.html")