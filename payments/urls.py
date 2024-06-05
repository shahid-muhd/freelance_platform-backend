from django.urls import path
from .views import SubscriptionManagerView,CreateCheckoutSession,WebHook,PrePayment


urlpatterns = [
    path(
        "subscriptions/", SubscriptionManagerView.as_view(), name="subscriptions"
    ),
    path('create-checkout-session/' , CreateCheckoutSession.as_view(),name='create-checkout-session'),
        path('webhook-stripe/' , WebHook.as_view()), 
    
    path(
        "pre-payment-details/", PrePayment.as_view(), name="pre-payment-details"
    ),
]
