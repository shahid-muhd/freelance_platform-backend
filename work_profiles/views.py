import json
from .models import WorkProfile
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import PortfolioSerializer, WorkProfileSerializer
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated


class WorkProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def list(self, request):
        user = request.user
        work_profiles = WorkProfile.objects(user=user.id)

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

        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
