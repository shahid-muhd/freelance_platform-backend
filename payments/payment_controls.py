from .serializers import SubscriptionSerializer
from accounts.models import CustomUser
from stripe import Subscription, Product
from .models import Subscription as SubscriptionModel
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from projects.models import Project, Proposals
from .serializers import ProjectPaymentSerializer, FreelancerPayoutSerializer


def subscription_creation_manager(**data):

    user = CustomUser.objects.get(email=data["user"])
    subscription_data = Subscription.retrieve(data["subscription_id"])
    product_id = subscription_data["items"]["data"][0]["plan"]["product"]
    product = Product.retrieve(product_id)
    product_name = product.metadata.product_identifier

    data["user"] = user.id
    data["package_name"] = product_name
    data["package_id"] = product_id

    try:
        existing_subscription = SubscriptionModel.objects.get(
            user_id=user.id, is_active=True, package_name=product_name
        )

    except SubscriptionModel.DoesNotExist:
        new_subscription = SubscriptionSerializer(data=data)
        if new_subscription.is_valid():
            new_subscription.save()
            condition_active = Q(is_active=True)
            condition_product_name = ~Q(package_name=product_name)
            condition_user = Q(user_id=user.id)
            query = condition_active & condition_product_name & condition_user
            try:
                existing_subscription = SubscriptionModel.objects.get(query)
                existing_projects_availability = existing_subscription.projects_left

                new_subscription = SubscriptionModel.objects.get(
                    subscription_id=data["subscription_id"]
                )
                new_subscription.projects_left = (
                    new_subscription.projects_left + existing_projects_availability
                )
                existing_subscription.is_active = False
                existing_subscription.projects_left = 0
                existing_subscription.save()
                new_subscription.save()
            except Exception as e:
                print(e)
            return True
        return new_subscription.errors


def client_payment_manager(**data):
    try:

        project = Project.objects.get(id=data["project"])
        freelancer_id = project.freelancer_id
        client_id = project.client_id
        payment_type = data["payment_type"]
        data["freelancer"] = freelancer_id
        data["client"] = client_id
        proposal = Proposals.objects.get(
            applicant_id=freelancer_id, project_id=data["project"]
        )
        data["proposal"] = proposal.id
        new_client_payment = ProjectPaymentSerializer(data=data)

        if new_client_payment.is_valid():
            new_client_payment.save()

            if payment_type == "advance":
                proposal.is_advance_paid = True
                proposal.save()
                project.status = "completed"
                project.is_advance_paid = True
                project.save()
            if payment_type == "final":

                payout_data = {
                    "freelancer": freelancer_id,
                    "payment_type": payment_type,
                    "client_payment_details": new_client_payment.instance.id,
                }

                new_payout = FreelancerPayoutSerializer(data=payout_data)
                if new_payout.is_valid():
                    new_payout.save()
                    if payment_type == "advance":
                        project.is_sample_completed = True
                    if payment_type == "final":
                        project.is_final_completed = True
                    project.save()

        else:
            print(new_client_payment.errors)
            raise Exception(new_client_payment.errors)
    except Exception as e:
        print(e)
