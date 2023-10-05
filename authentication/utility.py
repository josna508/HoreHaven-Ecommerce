# authentication/utility.py

import random
from twilio.rest import Client
from django.conf import settings

def send_otp(phone_number):
    # Generate a random 6-digit OTP
    otp = ''.join(random.choices('0123456789', k=6))

    # Initialize the Twilio client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Send OTP via Twilio
    message = client.messages.create(
        body=f'Your OTP for verification is: {otp}',
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return otp
