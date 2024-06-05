from django.shortcuts import render
from .models import Messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.utils import generate_video_chat_token
from .utils import get_exchangers
import json

class ExchangerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exchangers=get_exchangers(request.user.id)
        exchangers=json.dumps(exchangers)
        return Response(data=exchangers,status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getVideoChatToken(request):
     
     token =generate_video_chat_token(request.user.id)
     print('my token >>>>>>>',token)
     return Response(data=token,status=status.HTTP_200_OK)
   
