"""
Configuration file for Re:Gain Telegram Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",") if os.getenv("ADMIN_IDS") else []

# Token Logic (from survey validation)
TOKEN_SYSTEM = {
    "reuse": 10,           # Personal containers/bags
    "recycle_plastics": 5, # 10 plastics
    "recycle_cans": 5,     # 5 tins/cans
    "recycle_paper": 2,    # 50g paper
    "reduce": 1            # Opting out of plastic cutlery
}

# Target threshold
TARGET_TOKENS = 30

# Database
DATABASE_FILE = "regain_bot.db"

# States
class UserState:
    MAIN_MENU = "main_menu"
    REGISTERING = "registering"
    AWAITING_MATRIC = "awaiting_matric"
    SELECTING_CATEGORY = "selecting_category"
    AWAITING_PHOTO = "awaiting_photo"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    ADMIN_PANEL = "admin_panel"
    VIEWING_PENDING = "viewing_pending"
