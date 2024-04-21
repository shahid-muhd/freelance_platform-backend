import requests
from os import getenv
import jwt
from collaborator import settings
from .models import UnverifiedEmails, CustomUser
import random

# The key from one of your Verification Apps, found here https://dashboard.sinch.com/verification/apps
applicationKey = getenv("SINCH_APPLICATION_KEY")

# The secret from the Verification App that uses the key above, found here https://dashboard.sinch.com/verification/apps
applicationSecret = getenv("SINCH_APPLICATION_SECRET")


def request_phone_verification(number):

    # The number that will receive the SMS. Test accounts are limited to verified numbers.
    # The number must be in E.164 Format, e.g. Netherlands 0639111222 -> +31639111222

    sinchVerificationUrl = (
        "https://verification.api.sinch.com/verification/v1/verifications"
    )

    payload = {
        "identity": {"type": "number", "endpoint": number},
        "method": "sms",
        "message": "Verification Code From Loomix Collaborator",
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        sinchVerificationUrl,
        json=payload,
        headers=headers,
        auth=(applicationKey, applicationSecret),
    )

    data = response.json()
    return data


def verify_phone_number(number, code):
    try:
        sinchVerificationUrl = (
            "https://verification.api.sinch.com/verification/v1/verifications/number/"
            + number
        )

        payload = {"method": "sms", "sms": {"code": code}}

        headers = {"Content-Type": "application/json"}

        response = requests.put(
            sinchVerificationUrl,
            json=payload,
            headers=headers,
            auth=(applicationKey, applicationSecret),
        )

        data = response.json()
       
        if data["status"]:
            return True
        raise Exception
    except Exception as e:
        return False



def verification_token_generator(email):
    verification_token = jwt.encode(
        {"email": email}, settings.SECRET_KEY, algorithm="HS256"
    )

    return verification_token



def email_verifier(**kwargs):
    token = kwargs.get("token")
    email = kwargs.get("email")

    if email is None and token is not None:

        # Verifies an email
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_email = decoded_token["email"]

        matching_document = UnverifiedEmails.objects(user_email=token_email).first()
        if matching_document:
            matching_document.is_verified = True
            matching_document.save()
            return matching_document.user_email
        return False

    # Checks if an email is verified in temporary collection
    if email is not None:
        matching_document = UnverifiedEmails.objects(user_email=email).first()
        if matching_document and matching_document.is_verified == True:

            return True
        return False

    return None


def generate_otp():
    otp = ""

    for _ in range(6):
        otp += str(random.randint(0, 9))
    return otp


def verify_otp(**kwargs):
    email = kwargs.get("email")
    phone = kwargs.get("phone")
    otp = kwargs.get("otp")

    try:
        if email is not None:
            matching_document = UnverifiedEmails.objects(
                user_email=email, otp=otp
            ).first()
            return True

        matching_document = UnverifiedEmails.objects(phone=phone, otp=otp).first()
        return True
    except:
        return False