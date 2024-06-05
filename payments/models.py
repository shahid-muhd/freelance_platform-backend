from django.db import models
from accounts.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from projects.models import Project,Proposals

# Create your models here.


class ProjectPayments(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ("advance", "advance"),
        ("final", "final"),
    ]

    client = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    freelancer = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name="project_payments_freelancer"
    )
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    payment_id = models.CharField(max_length=255)
    price_id = models.CharField(max_length=155)
    amount = models.IntegerField()
    proposal=models.ForeignKey(Proposals,on_delete=models.DO_NOTHING)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    invoice_url = models.URLField(help_text="Invoice URL", null=True, blank=True)
    


class FreelancerPayouts(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ("advance", "advance"),
        ("final", "final"),
    ]

    freelancer = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    client_payment_details=models.ForeignKey(ProjectPayments,on_delete=models.PROTECT)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_date = models.DateTimeField(default=timezone.now)


class ClientRefunds(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ("advance", "advance"),
        ("final", "final"),
    ]
    client=models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    project_payment_details=models.ForeignKey(ProjectPayments,on_delete=models.PROTECT)
    payment_date = models.DateTimeField(default=timezone.now)
    

class Subscription(models.Model):

    def calculate_validity(self, package_name):
        if package_name == "standard":
            validity = timezone.now() + timedelta(days=30 * 6)
        else:
            validity = timezone.now() + timedelta(days=365)
        return validity.strftime("%Y-%m-%d")

    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    subscribed_date = models.DateTimeField(default=timezone.now)
    package_name = models.CharField(max_length=35)
    package_id = models.CharField(max_length=255)
    subscription_id = models.CharField(max_length=255)
    projects_left = models.IntegerField(default=10)
    invoice_url = models.URLField(help_text="Invoice URL", null=False, blank=False)
    validity = models.DateField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.validity:
            self.validity = self.calculate_validity(self.package_name)
        super(Subscription, self).save(*args, **kwargs)


class StripeProduct(models.Model):
    project=models.ForeignKey(Project,on_delete=models.DO_NOTHING)
    product_id=models.CharField(max_length=155)
    advance_pricing_id=models.CharField(max_length=155)
    final_pricing_id=models.CharField(max_length=155)
    freelancer=models.ForeignKey(CustomUser,on_delete=models.PROTECT)
    is_advance_paid=models.BooleanField(default=False)
    is_final_paid=models.BooleanField(default=False)
