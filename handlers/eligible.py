"""
Eligible users command for admins
"""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import Database
from config import ADMIN_IDS

db = Database()

async def eligible_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all users who are starpoint eligible"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ You don't have admin access.")
        return
    
    eligible = db.get_eligible_users()
    
    if not eligible:
        await update.message.reply_text("📊 No eligible users yet!")
        return
    
    message = f"⭐ *Starpoint Eligible Users* ({len(eligible)})\n\n"
    
    for user in eligible:
        message += (
            f"👤 {user['full_name']}\n"
            f"   Matric: {user['matric_number']}\n"
            f"   Tokens: {user['total_tokens']}\n"
            f"   ID: {user['user_id']}\n\n"
        )
    
    await update.message.reply_text(message, parse_mode='Markdown')
