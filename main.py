"""
Main Telegram Bot for IIUM Re:Gain Initiative
"""
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, CallbackQueryHandler
)
from config import BOT_TOKEN, UserState, ADMIN_IDS
from database.db import Database

# Initialize database
db = Database()

# Handlers
from handlers.start import (
    start_command, help_command, stats_command, MATRIC_INPUT
)
from handlers.register import (
    matric_handler, name_handler, cancel_registration,
    NAME_INPUT
)
from handlers.submit import (
    submit_action, category_handler, photo_handler, 
    confirm_submission, cancel_submission,
    CATEGORY_SELECTION, PHOTO_UPLOAD, CONFIRMATION
)
from admin.panel import (
    admin_panel, approve_submission_callback, 
    reject_submission_callback, skip_reason_callback, cancel_reject_callback,
    handle_rejection_reason, view_photo, verify_stats
)
from handlers.eligible import eligible_users

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_messages(update: Update, context):
    """Handle all text messages - route appropriately"""
    text = update.message.text
    user_id = update.effective_user.id
    
    # First check if this is a rejection reason
    if context.user_data.get('awaiting_reject_reason'):
        await handle_rejection_reason(update, context)
        return
    
    # Otherwise handle as button click
    if db.user_exists(user_id):
        if text == "📤 Submit Action":
            # Let submission_handler catch this - don't process here
            return
        elif text == "📊 View Progress":
            await stats_command(update, context)
        elif text == "❓ How it Works":
            await help_command(update, context)
        elif text == "🆘 Help":
            await help_command(update, context)
    else:
        await update.message.reply_text("❌ Please register first with /start")

def main():
    """Main function to run the bot"""
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not configured! Set it in .env file")
        return
    
    # Create the Application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mystats", stats_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("eligible", eligible_users))
    
    # Registration conversation handler - ONLY triggered by /start
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            MATRIC_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, matric_handler)],
            NAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel_registration)],
    )
    
    # Submission conversation handler
    submission_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex("^📤 Submit Action$"), submit_action)
        ],
        states={
            CATEGORY_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_handler)],
            PHOTO_UPLOAD: [MessageHandler(filters.PHOTO, photo_handler)],
            CONFIRMATION: [CallbackQueryHandler(confirm_submission, pattern="^confirm_submit$"),
                          CallbackQueryHandler(cancel_submission, pattern="^cancel_submit$")],
        },
        fallbacks=[CommandHandler("cancel", cancel_submission)],
    )
    
    # Add conversation handlers (order matters!)
    app.add_handler(registration_handler)
    app.add_handler(submission_handler)  # Must be BEFORE handle_messages
    
    # Callback query handlers
    app.add_handler(CallbackQueryHandler(view_photo, pattern="^view_photo_"))
    app.add_handler(CallbackQueryHandler(approve_submission_callback, pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(reject_submission_callback, pattern="^reject_"))
    app.add_handler(CallbackQueryHandler(skip_reason_callback, pattern="^skip_reason_"))
    app.add_handler(CallbackQueryHandler(cancel_reject_callback, pattern="^cancel_reject$"))
    
    # Unified message handler for buttons and rejection reasons
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    # Start the bot
    logger.info("✅ Bot started! Polling for updates...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
