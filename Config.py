import os

# Bot Configuration
BOT_TOKEN = "8743017124:AAFty35V7dJCOEQhTYRfaqB7YjOtqRfeXlI"  # Replace with your bot token
ADMIN_USER_ID = 6798566345  # Replace with your Telegram user ID

# API Endpoints
API_TG_TO_NUMBER = "https://tgchatid.vercel.app/api/lookup?number={query}"
API_GST = "https://toxic-eight.vercel.app/gst?number={query}"
API_VEHICLE = "https://toxic-vehical.vercel.app/api/vehicle-info?rc={query}"
API_IFSC = "https://ab-ifscinfoapi.vercel.app/info?ifsc={query}"

# Points cost per service
SERVICE_COST = {
    "tg_to_number": 1,
    "vehicle": 1,
    "gst": 1,
    "ifsc": 1,
}

# Default points for new users
DEFAULT_POINTS = 1
