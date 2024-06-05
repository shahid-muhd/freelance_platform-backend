from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .serializers import SubscriptionSerializer, StripeProductSerializer,FreelancerPayoutSerializer
import os
import stripe
from django.shortcuts import redirect
from .payment_controls import subscription_creation_manager, client_payment_manager
from .models import Subscription as SubscriptionModel
from .models import StripeProduct,FreelancerPayouts,ProjectPayments

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class SubscriptionManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_id = request.user.id
            subscription_existing = SubscriptionModel.objects.get(
                user_id=user_id, is_active=True
            )
            subscription_existing = SubscriptionSerializer(subscription_existing)

            return Response(data=subscription_existing.data, status=status.HTTP_200_OK)
        except SubscriptionModel.DoesNotExist:
            return Response(
                data="Does not have any subscriptions",
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

    def post(self, request):
        subscription_type = request.data["subscription_type"]

        return Response(status=status.HTTP_200_OK)


class CreateCheckoutSession(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        dataDict = dict(request.data)
        # price = dataDict["price"]
        # price = price * 100
        price_id = dataDict["pricing_name"]
        product_type = dataDict["product_type"]

        try:
            print("first rint in checkout")
            checkout_session = stripe.checkout.Session.create(
                line_items=[{"price": price_id, "quantity": 1}],
                payment_method_types=["card"],
                mode=product_type,
                success_url="http://localhost:3000/payments/result/success",
                cancel_url="http://localhost:3000/payments/result/failure",
                customer_email=request.user.email,
            )
            return Response(checkout_session.url, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(str(e))


class WebHook(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        event = None
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
        except ValueError as err:
            # Invalid payload
            raise err
        except stripe.error.SignatureVerificationError as err:
            # Invalid signature
            raise err

        # Handle the event
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            # print("<<<<payment_intent.succeeded>>>", payment_intent)

            # charge = payment_intent.get("latest_charge")
            # charge = stripe.Charge.retrieve(charge)
            # print("THE CHARGEEEEE>>>>>", charge)
        elif event.type == "payment_method.attached":
            payment_method = event.data.object
            # print("<<<<payment_method.attached>>>", payment_method)
        elif event.type == "invoice.payment_succeeded":
            invoice_succeeded = event.data.object
            # print("<<<<invoice.payment_succeeded>>>", invoice_succeeded)

        elif event.type == "invoice.updated":
            invoice_updated = event.data.object
            # print("<<<<invoice.updated>>>", invoice_updated)

        elif event.type == "invoice.paid":
            invoice_paid = event.data.object

            # data = {
            #     "user": invoice_paid["customer_email"],
            #     "invoice_url": invoice_paid["hosted_invoice_url"],
            #     "subscription_id": invoice_paid["subscription"],
            # }

            # SubscriptionCreationManager(**data)
        elif event.type == "checkout.session.completed":
            session_data = event.data.object

            payment_status = session_data.get("payment_status")
            payment_mode = session_data.get("mode")
            if payment_status == "paid":
                data = {
                    "user": session_data["customer_email"],
                }
                if payment_mode == "subscription":
                    invoice = stripe.Invoice.retrieve(session_data["invoice"])
                    data["invoice_url"] = invoice.hosted_invoice_url
                    data["subscription_id"] = (session_data["subscription"],)
                    subscription_creation_manager(**data)
                else:
                    session_id = session_data.get("id")

                    print("____Line ITEMS___________________________________________")
                    line_items = stripe.checkout.Session.list_line_items(session_id)
                    print("line >>>", line_items)
                    price_type = line_items["data"][0]["price"]["metadata"].get(
                        "price_type"
                    )
                    amount_cents = line_items["data"][0]["amount_subtotal"]
                    project_id = line_items["data"][0]["description"].split("_")[-1]
                    price_id = line_items["data"][0]["price"]["id"]

                    data = {
                        "payment_id": session_data.get("payment_intent"),
                        "amount": amount_cents / 100,
                        "payment_type": price_type,
                        "project": int(project_id),
                        "price_id": price_id,
                    }

                    client_payment_manager(**data)

        elif event.type == "charge.updated":
            charge_data = event.data.object

        else:
            print("Unhandled event type {}".format(event.type))

        return JsonResponse({"success": True}, safe=False)


class PrePayment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            project_id = request.query_params.get("data[project_id]")
            freelancer_id = request.query_params.get("data[user_id]")
    
            pre_payment_details = StripeProduct.objects.get(
                project_id=project_id, freelancer_id=freelancer_id
            )
            pre_payment_details = StripeProductSerializer(pre_payment_details)
            return Response(data=pre_payment_details.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)



class FreelancerPayout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        
        freelancer_id=request.data['freelancer']
        project_id=request.data['project']
        payment_type=request.data['payment_type']
        
        try:
            project_payment=ProjectPayments.objects.get(project_id=project_id,freelancer_id=freelancer_id,payment_type=payment_type)
            
            payout_details={               
            'client_payment_details_id':project_payment,
            'payment_type':payment_type,
            'freelancer_id':freelancer_id
            }
            new_freelancer_payout=FreelancerPayoutSerializer(data=payout_details)
        
            if new_freelancer_payout.is_valid():
                new_freelancer_payout.save()

                return Response(status=status.HTTP_200_OK)

        except ProjectPayments.DoesNotExist:

            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)

        except Exception as e:
            print('err in freelancer ayout >>',e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    

    