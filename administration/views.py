from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer, EmptySerializer
from accounts.models import CustomUser
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def update(self, request, pk=None):
        user = self.get_object()
        print(user)
        if user.is_blocked:
            print("in")
            user.is_blocked = False
        else:
            user.is_blocked = True
        user.save()

        return Response(status=200)
