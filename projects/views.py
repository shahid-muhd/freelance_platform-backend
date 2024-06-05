from django.shortcuts import render
from django.db.models import Q

# Create your views here.
from rest_framework import viewsets, status
from .models import Project, Proposals, SavedProjects
from .serializers import ProjectSerializer, ProposalSerializer, SavedProjectSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from .signals import proposal_acceptance_signal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.db.models import Q
from payments.utils import create_stripe_product, delete_stripe_product
from payments.models import FreelancerPayouts, ProjectPayments, ClientRefunds
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from payments.serializers import FreelancerPayoutSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.filter(is_blocked=False)
        if "pk" not in self.kwargs:
            queryset = queryset.exclude(
                Q(client_id=self.request.user.id) | Q(is_archived=True)
            )
            query_param = self.request.query_params.get("query_param", None)

            if query_param and query_param != "":
                queryset = queryset.filter(Q(title__icontains=query_param))

        return queryset


class SavedProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            saved_projects = SavedProjects.objects.get(user_id=request.user.id)
            return Response(data=saved_projects, status=status.HTTP_200_OK)
        except:
            return Response(data="No saved projects", status=status.HTTP_200_OK)

    def post(self, request):
        data = {"project": request.data["project_id"], "user": request.user.id}
        saved_project = SavedProjectSerializer(data=data)
        if saved_project.is_valid():
            saved_project.save()
        return Response(status=status.HTTP_200_OK)


class ProposalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    queryset = Proposals.objects.all()
    serializer_class = ProposalSerializer

    def get_queryset(self):
        filter_condition = self.request.query_params.get("data[filter_condition]")
        filter_query = Q(status=filter_condition) if filter_condition else Q()

        proposal_type = self.request.query_params.get("data[type]")

        if proposal_type == "send":
            # Filter proposals where the applicant is the current user
            queryset = Proposals.objects.filter(
                Q(applicant_id=self.request.user.id) & filter_query
            )
        else:

            client_projects = Project.objects.filter(
                client_id=self.request.user.id
            ).values_list("id", flat=True)

            queryset = Proposals.objects.filter(
                Q(project_id__in=client_projects) & filter_query
            )

        return queryset

    def partial_update(self, request, *args, **kwargs):

        instance = self.get_object()
        new_status = request.data["status"]
        print(new_status)
        project = Project.objects.get(id=instance.project_id)
        if new_status == "accepted":

            proposal = Proposals.objects.filter(
                project_id=instance.project_id, status="accepted"
            )
            if proposal:
                return Response(
                    data="Another proposal was already accepted for this project.",
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            applicant = instance.applicant
            project.freelancer = applicant
            project.status = "progressing"

            stripe_response = create_stripe_product(
                project_id=project.id,
                project_title=project.title,
                budget=project.budget,
                client=project.client,
                freelancer_id=applicant.id,
            )
            if stripe_response == False:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        notification_description_status = new_status
        if new_status == "unanswered":
            project.status = "recruiting"
            notification_description_status = "revoked"
            delete_stripe_product(project)

            project.freelancer = None
        instance.status = new_status
        instance.save()
        project.save()
        data = {
            "user": request.user.id,
            "title": f"Proposal {new_status}",
            "description": f'Your Proposal for the project "{project.title}" has been {notification_description_status} by the client.',
        }
        proposal_acceptance_signal.send(sender=self.__class__, data=data)
        return Response(data=f"{new_status} Project", status=status.HTTP_202_ACCEPTED)


# Retrieve all the project of a user
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieveUserProjects(request):
    user = request.user
    try:
        projects = Project.objects.filter(
            Q(client_id=user.id) | Q(freelancer_id=user.id)
        )
        projects = ProjectSerializer(projects, many=True)
        return Response(data=projects.data, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response(data="No Projects", status=status.HTTP_204_NO_CONTENT)


class WorkContractView(APIView):
    permission_classes = [IsAuthenticated]

    # accept work
    def post(self, request):

        proposal_id = request.data["proposal_id"]
        work_type = request.data["type"]

        try:
            proposal = Proposals.objects.get(id=proposal_id)
            project = Project.objects.get(id=proposal.project_id)
            freelancer_id = proposal.applicant_id

            if work_type == "sample":
                payment_type = "advance"
            else:
                payment_type = "final"

            client_payments = ProjectPayments.objects.get(proposal_id=proposal_id)
            if FreelancerPayouts.objects.filter(
                client_payment_details_id=client_payments.id, payment_type=payment_type
            ).exists():
                return Response(status=status.HTTP_208_ALREADY_REPORTED)
            payout_data = {
                "freelancer": freelancer_id,
                "payment_type": payment_type,
                "client_payment_details": client_payments.id,
            }

            new_payout = FreelancerPayoutSerializer(data=payout_data)
            if new_payout.is_valid():
                new_payout.save()
                if work_type == "sample":
                    project.is_sample_completed = True
                if work_type == "final":
                    project.is_final_completed = True
                project.save()
            else:
                print(new_payout.errors)
            return Response(
                data=f"You have accepted the {work_type} work for this project",
                status=status.HTTP_200_OK,
            )
        except ProjectPayments.DoesNotExist as e:
            print(e)
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        current_user_id = request.user.id
        proposal_id = request.data["proposal_id"]
        proposal = Proposals.objects.get(id=proposal_id)
        project_id = proposal.project_id
        freelancer_id = proposal.applicant_id
        project = Project.objects.get(id=project_id, freelancer_id=freelancer_id)
        try:
            client_payment = ProjectPayments.objects.get(
                project_id=project_id, freelancer_id=freelancer_id
            )
            freelancer_payout = FreelancerPayouts.objects.get(
                client_payment_details_id=client_payment.id
            )

        except ProjectPayments.DoesNotExist:
            print(
                "not supposed to happen if user is client :project payment doesnt exist"
            )
            if current_user_id == proposal.applicant_id:
                print("same user")
                proposal.delete()
            else:
                proposal.is_advance_paid = False
                proposal.status = "unanswered"
                proposal.save()
            return Response(status=status.HTTP_200_OK)
        except FreelancerPayouts.DoesNotExist:
            proposal.is_advance_paid = False
            proposal.status = "unanswered"
            proposal.save()
            if current_user_id is not proposal.applicant_id:

                new_client_refund = ClientRefunds.objects.create(
                    client_id=client_payment.client_id,
                    payment_type="advance",  # or 'final'
                    project_payment_details_id=client_payment.id,
                )

            else:

                client_payment.delete()
                proposal.delete()
        project.freelancer = None
        project.is_advance_paid = False
        project.is_sample_completed = False
        project.save()

        return Response(status=status.HTTP_200_OK)
