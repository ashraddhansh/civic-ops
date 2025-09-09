import os
from dotenv import load_dotenv

# Load .env from parent folder
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# JWT & OTP config
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 1440))
OTP_EXPIRATION_MINUTES = int(os.getenv("OTP_EXPIRATION_MINUTES", 5))
