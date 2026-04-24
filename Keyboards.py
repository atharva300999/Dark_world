from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_all_channels

def get_channel_buttons():
    """Generate channel join buttons (supports both public and private)"""
    channels = get_all_channels()
    keyboard = []
    
    for channel_username, channel_type in channels:
        if channel_type == "public":
            # Public channel - direct link
            url = f"https://t.me/{channel_username}"
            button_text = f"📢 Join @{channel_username}"
        else:
            # Private channel - invite link
            url = channel_username
            button_text = f"🔒 Join Private Channel"
        
        keyboard.append([InlineKeyboardButton(button_text, url=url)])
    
    keyboard.append([InlineKeyboardButton("✅ Check", callback_data="check_join")])
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔍 Services", callback_data="services")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("🫂 Refer", callback_data="refer")],
        [InlineKeyboardButton("🎁 Gift Code", callback_data="gift_code")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_services_keyboard():
    keyboard = [
        [InlineKeyboardButton("📲 TG ID ➙ NUMBER", callback_data="service_tg")],
        [InlineKeyboardButton("🚗 VEHICLE NUM", callback_data="service_vehicle")],
        [InlineKeyboardButton("📜 GST NUM DETAILS", callback_data="service_gst")],
        [InlineKeyboardButton("🏦 IFSC INFO", callback_data="service_ifsc")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="services")]])
