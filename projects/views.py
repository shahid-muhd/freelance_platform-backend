from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    print('in viewset projexcts')
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
