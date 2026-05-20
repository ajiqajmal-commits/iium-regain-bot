"""
Start command handler
"""
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from database.db import Database

# States for registration flow
MATRIC_INPUT = 1

db = Database()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if user:
        # User already registered
        stats = db.get_user_stats(user_id)
        progress_bar = get_progress_bar(stats['total_tokens'], 30)
        await update.message.reply_text(
            f"Welcome back, {user['full_name'] or 'User'}! 🌍\n\n"
            f"📊 Your Progress:\n"
            f"• Total Tokens: {stats['total_tokens']}/30\n"
            f"{progress_bar}\n"
            f"• Status: {'✅ Starpoint Eligible!' if stats['starpoint_eligible'] else '⏳ Keep going!'}\n\n"
            f"What would you like to do?",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    else:
        # New user - start registration
        await update.message.reply_text(
            "🌱 Welcome to IIUM Re:Gain! 🌱\n\n"
            "A gamified platform to earn Starpoints through sustainable 3R practices:\n"
            "♻️ Recycle • 🔄 Reuse • ⬇️ Reduce\n\n"
            "Let's get started! Please enter your Matric Number to register.",
            reply_markup=ReplyKeyboardRemove()
        )
        return MATRIC_INPUT

def get_main_menu_keyboard():
    """Get main menu with inline buttons"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📤 Submit Action", callback_data="menu_submit"),
            InlineKeyboardButton("📊 My History", callback_data="menu_history")
        ],
        [
            InlineKeyboardButton("📈 My Stats", callback_data="menu_stats"),
            InlineKeyboardButton("❓ How it Works", callback_data="menu_help")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="menu_leaderboard")
        ]
    ])

def get_progress_bar(current: int, target: int) -> str:
    """Generate a visual progress bar"""
    filled = min(current * 10 // target, 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"`{bar}` {current}/{target}"

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🆘 *Need Help?*

*Commands:*
/start - Go back to main menu
/help - Show this message
/mystats - View your progress

*Token System:*
• 🔄 Reuse (personal containers/bags) = +10 tokens
• ♻️ Recycle plastics (10 items) = +5 tokens
• ♻️ Recycle cans (5 items) = +5 tokens
• ♻️ Recycle paper (50g) = +2 tokens
• ⬇️ Reduce (no plastic cutlery) = +1 token

*Goal:*
Earn 30 tokens → Get Starpoints! ⭐

*How to submit:*
1. Click "📤 Submit Action"
2. Choose action category
3. Upload photo as proof
4. Wait for admin verification
5. Get tokens!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mystats command"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("❌ You're not registered yet. Use /start to register!")
        return
    
    stats = db.get_user_stats(user_id)
    progress_bar = get_progress_bar(stats['total_tokens'], 30)
    
    stats_text = f"""
📊 *Your Progress*

*Username:* {user['full_name'] or 'N/A'}
*Matric Number:* {user['matric_number']}

*Tokens:* {stats['total_tokens']}/30
{progress_bar}

*Submissions:*
✅ Approved: {stats['approved_count']}
⏳ Pending: {stats['pending_count']}
❌ Rejected: {stats['rejected_count']}

*Status:* {'🎉 Starpoint Eligible!' if stats['starpoint_eligible'] else '⏳ Keep submitting!'}
"""
    await update.message.reply_text(stats_text, parse_mode='Markdown')

def get_progress_bar(current: int, total: int) -> str:
    """Generate progress bar"""
    filled = int((current / total) * 10)
    bar = '█' * filled + '░' * (10 - filled)
    return f"`{bar}` {current}/{total}"
