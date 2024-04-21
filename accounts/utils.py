from .models import CustomUser


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
