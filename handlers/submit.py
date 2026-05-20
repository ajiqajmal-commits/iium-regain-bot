"""
Submission handler for user actions
"""
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from config import TOKEN_SYSTEM
from database.db import Database

db = Database()

# Conversation states
CATEGORY_SELECTION = 1
PHOTO_UPLOAD = 2
CONFIRMATION = 3

CATEGORY_BUTTONS = [
    ['🔄 Reuse', '♻️ Recycle Plastic'],
    ['🥫 Recycle Cans', '📄 Recycle Paper'],
    ['⬇️ Reduce', '❌ Cancel']
]

CATEGORY_MAP = {
    '🔄 Reuse': 'reuse',
    '♻️ Recycle Plastic': 'recycle_plastics',
    '🥫 Recycle Cans': 'recycle_cans',
    '📄 Recycle Paper': 'recycle_paper',
    '⬇️ Reduce': 'reduce'
}

CATEGORY_DESCRIPTIONS = {
    'reuse': ('🔄 Reuse', 'Using personal containers/bags', 10),
    'recycle_plastics': ('♻️ Recycle Plastic', 'Recycling 10 plastic items', 5),
    'recycle_cans': ('🥫 Recycle Cans', 'Recycling 5 cans/tins', 5),
    'recycle_paper': ('📄 Recycle Paper', 'Recycling 50g of paper', 2),
    'reduce': ('⬇️ Reduce', 'Opting out of plastic cutlery', 1)
}

def show_category_buttons():
    """Get category selection as inline buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Reuse", callback_data="cat_reuse")],
        [InlineKeyboardButton("♻️ Plastic", callback_data="cat_recycle_plastics")],
        [InlineKeyboardButton("🥫 Cans", callback_data="cat_recycle_cans")],
        [InlineKeyboardButton("📄 Paper", callback_data="cat_recycle_paper")],
        [InlineKeyboardButton("⬇️ Reduce", callback_data="cat_reduce")],
    ])

async def submit_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start submission process"""
    user_id = update.effective_user.id
    
    if not db.user_exists(user_id):
        await update.message.reply_text(
            "❌ You must register first! Use /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "What type of action did you perform?",
        reply_markup=ReplyKeyboardMarkup(CATEGORY_BUTTONS, resize_keyboard=True)
    )
    return CATEGORY_SELECTION

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection"""
    choice = update.message.text
    
    if choice == '❌ Cancel':
        await update.message.reply_text(
            "Submission cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    if choice not in CATEGORY_MAP:
        await update.message.reply_text(
            "❌ Invalid choice. Please select from the options:",
            reply_markup=ReplyKeyboardMarkup(CATEGORY_BUTTONS, resize_keyboard=True)
        )
        return CATEGORY_SELECTION
    
    category = CATEGORY_MAP[choice]
    emoji, description, tokens = CATEGORY_DESCRIPTIONS[category]
    
    context.user_data['category'] = category
    context.user_data['tokens'] = tokens
    
    await update.message.reply_text(
        f"📸 *{emoji} {description}*\n\n"
        f"Please upload a photo as proof of your action.\n"
        f"You'll get *+{tokens} tokens* if approved! 🎯",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )
    return PHOTO_UPLOAD

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo upload"""
    if not update.message.photo:
        await update.message.reply_text("❌ Please upload a photo.")
        return PHOTO_UPLOAD
    
    photo_file_id = update.message.photo[-1].file_id
    context.user_data['photo_file_id'] = photo_file_id
    
    category = context.user_data['category']
    tokens = context.user_data['tokens']
    emoji, description, _ = CATEGORY_DESCRIPTIONS[category]
    
    # Create confirmation
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Submit", callback_data=f"confirm_submit"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_submit")
        ]
    ])
    
    await update.message.reply_text(
        f"*Confirm Submission*\n\n"
        f"Category: {emoji} {description}\n"
        f"Tokens: +{tokens}\n\n"
        f"Is this correct?",
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    return CONFIRMATION

async def confirm_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and create submission"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    category = context.user_data.get('category')
    photo_file_id = context.user_data.get('photo_file_id')
    tokens = context.user_data.get('tokens')
    
    if not all([category, photo_file_id, tokens]):
        await query.edit_message_text("❌ Error. Please try again.")
        return ConversationHandler.END
    
    # Create submission
    submission_id = db.create_submission(user_id, category, photo_file_id, tokens)
    
    await query.edit_message_text(
        f"✅ *Submission Received!*\n\n"
        f"Submission ID: #{submission_id}\n"
        f"Tokens Pending: +{tokens}\n\n"
        f"Admin will review your submission soon. Check your stats with /mystats",
        parse_mode='Markdown'
    )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel submission"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ Submission cancelled."
    )
    
    context.user_data.clear()
    return ConversationHandler.END
