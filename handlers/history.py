"""
Submission history command for users
"""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import Database

db = Database()

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's submission history"""
    user_id = update.effective_user.id
    
    # Check if user is registered
    if not db.user_exists(user_id):
        await update.message.reply_text("❌ Please register first with /start")
        return
    
    submissions = db.get_user_submissions(user_id)
    
    if not submissions:
        await update.message.reply_text("📋 No submissions yet!\n\nUse 📤 Submit Action to get started.")
        return
    
    emoji_map = {
        'reuse': '🔄',
        'recycle_plastics': '♻️',
        'recycle_cans': '🥫',
        'recycle_paper': '📄',
        'reduce': '⬇️'
    }
    
    status_emoji = {
        'pending': '⏳',
        'approved': '✅',
        'rejected': '❌'
    }
    
    message = f"📋 *Your Submissions* ({len(submissions)})\n\n"
    
    for sub in submissions:
        emoji = emoji_map.get(sub['category'], '📌')
        status = status_emoji.get(sub['status'], '❓')
        
        message += (
            f"{status} Submission #{sub['submission_id']}\n"
            f"   {emoji} {sub['category']}\n"
            f"   Tokens: +{sub['tokens_awarded']}\n"
            f"   Date: {sub['created_at']}\n"
        )
        
        if sub['verified_at']:
            message += f"   Verified: {sub['verified_at']}\n"
        
        message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')
