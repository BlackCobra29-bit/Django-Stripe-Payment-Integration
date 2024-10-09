from django.contrib import admin
from django.urls import path
from payment import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("tutorial-list", views.tutorial_list, name="tutorial-list"),
    path("checkout/<int:tutorial_id>", views.stripe_checkout, name="tutorial-checkout"),
    path("stripe-webhook", views.webhook_manager, name = "webhook-manager"),
    path("payment-success/", views.payment_success, name = "payment-success"),
    path("payment-cancel/", views.payment_cancel, name = "payment-cancel")
]