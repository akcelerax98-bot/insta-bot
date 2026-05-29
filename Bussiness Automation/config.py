import os
from dotenv import load_dotenv

load_dotenv()

# Instagram
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
INSTAGRAM_SESSION_ID = os.getenv("INSTAGRAM_SESSION_ID")

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
_raw_numbers = os.getenv("MY_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBERS = [n.strip() for n in _raw_numbers.split(",")] if _raw_numbers else []

# Database
DB_NAME = "outreach.db"

# Outreach Settings
OUTREACH_LIMIT = 5
SEARCH_HASHTAGS = ["ecommerce", "onlinestore", "shopify", "boutique", "smallbusiness"]

# Messages
OUTREACH_MESSAGE = """Hi 👋

We came across your page and loved what you're building 🚀

We provide a Virtual Assistant 🤖 that can take care of repetitive business tasks automatically.

Tell us your biggest business challenge 💭, and we'll create a solution tailored to your needs ⚡

We also share business growth ideas 📈 and marketing strategies 🎯 if you're interested."""

AUTO_REPLY_MESSAGE = """Thank you for your response 🙌

We appreciate your interest.

Our team will review your message and DM you soon today 🚀"""
