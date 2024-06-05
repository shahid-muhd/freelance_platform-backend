import jwt
import time
from .models import CustomUser
import os


def check_email_existence(email):

    try:
        CustomUser.objects.get(email=email)
        return True
    except:

        return False


def mail_html_content_config(token):

    mail_html_content = f"""<!DOCTYPE html>
                           <html lang="en">
                           <head>
                               <meta charset="UTF-8">
                               <meta http-equiv="X-UA-Compatible" content="IE=edge">
                               <meta name="viewport" content="width=device-width, initial-scale=1.0">
                               <title>Email Verification</title>
                           </head>
                           <body>
                               <p>Dear User,</p>
                               <p>Please click the button below to verify your email address for Loomix account:</p>
                               <a href="http://localhost:8000/auth/register?token={token}" style="display: inline-block; background-color: #007bff; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
                               <p>This link will expire automatically after 5 minutes</p>
                               <p>If you didn't request this, you can safely ignore this email.</p>
                           </body>
                           </html>"""

    return mail_html_content


app_id = os.getenv("ZEGOCLOUD_APP_SIGN")
server_secret = str(os.getenv("ZEGOCLOUD_SERVER_SECRET"))


def generate_video_chat_token(user_id):
    if not isinstance(server_secret, str):
        raise TypeError("Expected the server_secret to be a string")

    payload = {
        "app_id": app_id,
        "user_id": user_id,
        "nonce": int(time.time() * 1000),
        "expired_at": int(time.time()) + 3600,
        "privileges": {
            "room:join": True,
            "stream:publish": True,
            "stream:play": True,
        },
    }

    token = jwt.encode(payload, server_secret, algorithm="HS256")
    return token
