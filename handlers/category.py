"""
Category selection callback handler
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database.db import Database
from handlers.submit import CATEGORY_DESCRIPTIONS

db = Database()

async def category_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection from inline buttons"""
    query = update.callback_query
    print(f"DEBUG: category_selection_callback called with data: {query.data}")
    await query.answer()
    
    # Extract category from callback data (e.g., "cat_reuse" → "reuse")
    category = query.data.split("_", 1)[1]
    
    # Validate category
    if category not in CATEGORY_DESCRIPTIONS:
        await query.edit_message_text("❌ Invalid category selection")
        return
    
    # Store in context
    emoji, description, tokens = CATEGORY_DESCRIPTIONS[category]
    context.user_data['category'] = category
    context.user_data['tokens'] = tokens
    context.user_data['awaiting_photo'] = True
    
    # Ask for photo
    await query.edit_message_text(
        f"📸 *{emoji} {description}*\n\n"
        f"Please upload a photo as proof of your action.\n"
        f"You'll get *+{tokens} tokens* if approved! 🎯",
        parse_mode='Markdown'
    )
