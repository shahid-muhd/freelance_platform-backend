import os
import stripe
from .serializers import StripeProductSerializer

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = "your_secret_key"
from projects.models import Project, Proposals
from .models import StripeProduct,FreelancerPayouts,ProjectPayments


def create_stripe_product(**data):
    project_id = data.get("project_id")
    project_title = data.get("project_title")
    client = data.get("client")
    freelancer_id = data.get("freelancer_id")
    budget = data.get("budget")
    product_data = {
        "name": f"Project_{project_id}",
        "description": project_title,
        # "id": f"{project_id}",
        "metadata": {
            "project_id": f"{project_id}",
            "client_id": f"{client}",
            "freelancer_id": f"{freelancer_id}",
        },
    }
    try:
        product = stripe.Product.create(**product_data)
        advance_amount = budget * 0.10
        final_amount=budget-advance_amount

        price_data = {
            "unit_amount": int(final_amount * 100),
            "currency": "usd",
            "product": product.id,
            "metadata": {
                "price_type": "final",
            },
        }

        final_price = stripe.Price.create(**price_data)


        price_data["unit_amount"] = int(advance_amount * 100)
        price_data["metadata"]["price_type"] = "advance"

        advance_price = stripe.Price.create(**price_data)

        model_data = {
            "project": project_id,
            "product_id": product.id,
            "advance_pricing_id": advance_price.id,
            "final_pricing_id": final_price.id,
            "freelancer": freelancer_id,
        }

        new_stripe_product = StripeProductSerializer(data=model_data)

        if new_stripe_product.is_valid():

            new_stripe_product.save()
            return True
    except Exception as e:
        print("<<<<<<<exception in price creation>>>>>>>>", e)
        return False


def delete_stripe_product(project: Project):

    try:
        # Attempt to delete the product
        freelancer = project.freelancer_id
        print(">>>>>>>printinf data<<<<<<<<<<<<")
        print(freelancer)
        print(project.id)
        stripe_product = StripeProduct.objects.get(
            freelancer_id=freelancer, project_id=project.id
        )
        product = stripe.Product.modify(stripe_product.product_id, active=False)

        stripe_product.delete()
        proposal = Proposals.objects.get(applicant_id=freelancer, project_id=project.id)
        proposal.is_advance_paid = False
        proposal.save()

        print(f"Product '{product.name}' (ID: {product.id}) deleted successfully.")
    except stripe.error.InvalidRequestError as e:
        # Handle the case where the product has associated prices
        if e.error.code == "resource_missing":
            print("The product you're trying to delete doesn't exist.")
        elif e.error.code == "resource_has_dependent_objects":
            print(
                "This product cannot be deleted because it has associated prices. You'll need to delete the prices first."
            )
        else:
            print(f"An unexpected error occurred: {e}")
    except stripe.error.APIError as e:
        # Handle other potential API errors
        print(f"An API error occurred: {e}")





