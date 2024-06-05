import json
from .models import WorkProfile, Portfolio
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PortfolioSerializer, WorkProfileSerializer
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from projects.views import Proposals
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


class WorkProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    def list(self, request):

        user_specific = request.query_params.get("data[userSpecific]", False)

        user = request.user
        if user_specific:
            work_profiles = WorkProfile.objects(user=user.id, is_archived=False)
        else:
            work_profiles = WorkProfile.objects.all(is_archived=False)

        work_profiles = WorkProfileSerializer.serialize(self, work_profiles)

        return Response(work_profiles, status=status.HTTP_200_OK)

    def create(self, request):

        overview = json.loads(request.data.get("overview"))
        skills = json.loads(request.data.get("skills"))
        portfolios = json.loads(request.data.get("portfolios"))

        work_profile_data = overview
        work_profile_data.update(
            {
                "user": request.user.id,
                "skills": skills,
            }
        )

        new_work_profile = WorkProfile(**work_profile_data)
        new_work_profile.save()

        if isinstance(portfolios, list):
            for i in range(len(portfolios)):

                portfolio_data = portfolios[i]
                cover_image = request.data.get(f"portfolio_{i+1}_image")

                portfolio_data.update(
                    {
                        "work_profile": str(new_work_profile.id),
                        "cover_image": cover_image,
                    }
                )

                portfolio_serializer = PortfolioSerializer(data=portfolio_data)

                if portfolio_serializer.is_valid():
                    portfolio_serializer.save()
                else:
                    print("folio serializer error :", portfolio_serializer.errors)
                    return Response(
                        portfolio_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        work_profile = WorkProfile.objects(id=pk)
        work_profile = WorkProfileSerializer.serialize(self, work_profile)
        return Response(work_profile, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):

        work_profile = WorkProfile.objects.get(id=pk)

        work_profile.title = request.data["title"]
        work_profile.description = request.data["description"]
        work_profile.skills = request.data["skills"]

        work_profile.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        work_profile = WorkProfile.objects(id=pk)
        try:
            Proposals.objects.get(work_profile=pk)
            work_profile.is_archived = True
            work_profile.save()
            return Response(status=status.HTTP_200_OK)
        except Proposals.DoesNotExist:
            work_profile.delete()
            return Response(status=status.HTTP_200_OK)


class PortfolioViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

    def list(self, request):
        work_profile = request.query_params.get("workprofile")
        portfolios = Portfolio.objects.filter(work_profile=work_profile)
        portfolios = PortfolioSerializer(portfolios, many=True)
        return Response(data=portfolios.data, status=status.HTTP_200_OK)



