from django.shortcuts import redirect
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserSerializer, Addressserializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import UnverifiedEmails, CustomUser, Address
from .utils import (
    mail_html_content_config,
    check_email_existence,
)
from .verifications import (
    verification_token_generator,
    email_verifier,
    generate_otp,
    verify_otp,
    request_phone_verification,
    verify_phone_number,
)
import os

from rest_framework import status
from mongoengine.errors import NotUniqueError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
import base64
import uuid
from django.core.files.base import ContentFile


# view for registering users
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print(request.data)
            email = request.data["email"]

            if check_email_existence(email):
                print("existing email")
                return Response(
                    data="An account with the email already exists.",
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )

            try:
                otp_doc = UnverifiedEmails(user_email=email)
                otp_doc.save()

                verification_token = verification_token_generator(email)
                mail_html_content = mail_html_content_config(verification_token)

                send_mail(
                    "Loomix Account Verification",
                    "",
                    "",
                    [email],
                    fail_silently=False,
                    html_message=mail_html_content,
                )
            except NotUniqueError:
                return Response(status=status.HTTP_208_ALREADY_REPORTED)

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        token = request.GET.get("token")
        email = request.GET.get("email")

        if token:
            if email_verifier(token=token):
                return redirect("http://localhost:3000/auth/register/create-account")
            return redirect("http://localhost:3000/tg34tbb/")

        if email:
            if email_verifier(email=email):
                return Response(status=status.HTTP_200_OK)
            response = {"message": "Email not verified"}
            return Response(response, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def create_account(request):
    email = request.data["email"]
    print(request.data)
    if email_verifier(email=email):
        serialized_data = UserRegisterSerializer(data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response("Email verification timed out", status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        try:
            print("user id -->", user_id)

            if user_id is not None:
                user = CustomUser.objects.get(id=user_id)
                user_serialized = UserSerializer(user)

            else:
                user = request.user
                user_serialized = UserSerializer(user)
            address = Address.objects.get(user=user.id)
            address = Addressserializer(address)
            address = address.data
        except Address.DoesNotExist:
            address = None

        data = {"user": user_serialized.data, "address": address}
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request):

        data = request.data["data"]

        if "otp" in data:

            user = CustomUser.objects.get(id=request.user.id)
            otp = data["otp"]
            if "email" in data:

                email = data["email"]
                if verify_otp(email=email, otp=otp):

                    data = {"email": email}
                    serializer = UserSerializer(user, data=data, partial=True)
                    if serializer.is_valid():

                        serializer.save()

                        return Response(status=status.HTTP_200_OK)
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

            # Then phone is in data
            phone = data["phone"]
            if verify_phone_number(phone, otp):
                serializer_data = {"phone": phone}
                serializer = UserSerializer(user, data=serializer_data, partial=True)
                if serializer.is_valid():

                    serializer.save()
                    return Response(status=status.HTTP_200_OK)

            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        if "email" in data:
            generated_otp = generate_otp()
            email = data["email"]

            otp_doc = UnverifiedEmails(user_email=email, otp=generated_otp)
            otp_doc.save()

            send_mail(
                "Loomix Account Verification",
                f"OTP for email verification is : {generated_otp}",
                "",
                [email],
                fail_silently=False,
            )

            return Response(status=status.HTTP_200_OK)

        if "phone" in data:
            print("in phone verify request...")
            phone = data["phone"]

            response = request_phone_verification(phone)
            print("res from function verify", response)

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):

        user = CustomUser.objects.get(
            id=request.user.id
        )  # Example: Get the instance you want to update

        print("user data :", request.data)
        if "user" in request.data:
            data = request.data["user"]
            if "profile_image" in data:
                image_decoded = base64.b64decode(
                    data["profile_image"].split(";base64,")[1]
                )
                splitted_data = data["profile_image"].split("/")[1].split(";")
                extension = "." + splitted_data[0]
                file_name = str(uuid.uuid4())[:12]
                profile_image = ContentFile(image_decoded, name=file_name + extension)
                data["profile_image"] = profile_image

            print("image", data)
            serializer = UserSerializer(user, data=data, partial=True)
        if "address" in request.data:
            address_data = request.data["address"]
            address_data["user"] = user.id

            serializer = Addressserializer(data=request.data["address"])
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountRecovery(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            generated_otp = generate_otp()
            email = request.data["email"]
            if check_email_existence(email):
                otp_doc = UnverifiedEmails(user_email=email, otp=generated_otp)
                otp_doc.save()

                send_mail(
                    "Loomix Account Verification",
                    f"OTP for email verification is : {generated_otp}",
                    "",
                    [email],
                    fail_silently=False,
                )
            return Response(status=status.HTTP_200_OK)
        except NotUniqueError:
            return Response(status=status.HTTP_208_ALREADY_REPORTED)
        except Exception as e:
            print(f"{e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        otp = request.data["otp"]
        email = request.data["email"]
        password = request.data["password"]

        if verify_otp(email=email, otp=otp):
            user = CustomUser.objects.get(email=email)

            data = {"email": email, "password": password}
            serializer = UserRegisterSerializer(user, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response(status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print(f"{e}")
            return Response(status=status.HTTP_400_BAD_REQUEST)
