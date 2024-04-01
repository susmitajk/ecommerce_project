from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings

# Function to generate random 4 digit number
def generate_otp(length=4):
    return get_random_string(length, '1234567890')


# Function to send OTP through email
def send_otp_email(email, otp):
    subject = 'Verification OTP for Your Account'
    message = f'Your OTP for account verification is: {otp}'
    from_email = settings.EMAIL_HOST_USER  # Change this to your email address
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)