from rest_framework import serializers
from .models import Subscription, StripeProduct, ProjectPayments, FreelancerPayouts


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = "__all__"
        extra_kwargs = {"validity": {"read_only": True}}


class StripeProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = StripeProduct
        fields = "__all__"


class ProjectPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPayments
        fields = "__all__"


class FreelancerPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerPayouts
        fields = "__all__"
