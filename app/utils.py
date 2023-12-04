import secrets
import requests
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()


def encrypt(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode("utf-8"))
    encoded_data = sha256.hexdigest()
    return encoded_data


def generate_verification_token():
    token_length = 8
    return secrets.token_hex(token_length)


def send_verification_email(user, user_id):
    api_key = os.getenv("api_key")
    # print(f"******* api_key : {api_key} ************")
    domain = os.getenv("domain")

    url = f"https://api.mailgun.net/v3/{domain}/messages"

    verification_url = (
        f"http://127.0.0.1:5000/api/verify/{user.email}/{user.verification_token}"
    )

    # print(f"******* url : {url} ************")

    to = user_id
    msg = f"""Account Verification \n\n Howdy\n

Thank you for choosing EZ Technologies! Please confirm your email address by clicking 
the link below.
click or paste the link :  {verification_url}\n
If you did not sign up for a Mailgun account, you can simply disregard this email.
Happy Learning!
The EZ Technologies"""
    sub = f"Hi {user.name}, please verify your EZ Technologies account"
    # print(f"msg : {msg}")
    response = requests.post(
        url,
        auth=("api", api_key),
        data={
            "from": "noreply@ez.com",
            "to": to,
            "subject": sub,
            "text": msg,
        },
    )

    print(f"response : {response}")
