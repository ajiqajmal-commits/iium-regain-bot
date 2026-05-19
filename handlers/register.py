"""
Registration handler
"""
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from database.db import Database

db = Database()

# Conversation states
MATRIC_INPUT = 1
NAME_INPUT = 2

async def register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start registration process - only if not registered"""
    user_id = update.effective_user.id
    
    # Check if user is already registered
    if db.user_exists(user_id):
        # User already registered, don't enter registration flow
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Please enter your Matric Number (e.g., 2312821):",
        reply_markup=ReplyKeyboardRemove()
    )
    return MATRIC_INPUT

async def matric_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle matric number input"""
    matric_number = update.message.text.strip().upper()
    
    # Basic validation
    if len(matric_number) < 5:
        await update.message.reply_text(
            "❌ Invalid Matric Number. Please try again (e.g., 2312821):"
        )
        return MATRIC_INPUT
    
    # Check if already registered
    if db.get_user_by_matric(matric_number):
        await update.message.reply_text(
            "⚠️ This Matric Number is already registered. Use /start to access your account."
        )
        return ConversationHandler.END
    
    context.user_data['matric_number'] = matric_number
    
    await update.message.reply_text(
        "Great! Now, please enter your full name:"
    )
    return NAME_INPUT

async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle name input and complete registration"""
    full_name = update.message.text.strip()
    user_id = update.effective_user.id
    matric_number = context.user_data['matric_number']
    
    if len(full_name) < 3:
        await update.message.reply_text(
            "❌ Name too short. Please enter a valid name:"
        )
        return NAME_INPUT
    
    # Register user
    if db.register_user(user_id, matric_number, full_name):
        await update.message.reply_text(
            f"✅ *Registration Successful!*\n\n"
            f"Welcome, {full_name}! 🎉\n\n"
            f"Your Matric: {matric_number}\n\n"
            f"You can now start submitting your 3R actions to earn tokens!\n"
            f"Type /help to learn more.",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ Registration failed. Please try again."
        )
        return ConversationHandler.END

async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel registration"""
    await update.message.reply_text(
        "Registration cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
