"""
Main menu callbacks
"""
from telegram import Update
from telegram.ext import ContextTypes
from database.db import Database

db = Database()

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button clicks"""
    query = update.callback_query
    await query.answer()
    
    action = query.data.split("_", 1)[1]
    user_id = query.from_user.id
    
    if action == "submit":
        # Show submit action menu (with inline buttons for categories)
        from handlers.submit import show_category_buttons
        await query.edit_message_text(
            "📤 *Select Action Category*\n\n"
            "Choose what you did for the 3R initiative:",
            reply_markup=show_category_buttons()
        )
    
    elif action == "history":
        # Show submission history
        submissions = db.get_user_submissions(user_id)
        
        if not submissions:
            await query.edit_message_text("📋 No submissions yet!\n\nUse 📤 Submit Action to get started.")
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
                f"{status} #{sub['submission_id']}: {emoji} {sub['category']} "
                f"(+{sub['tokens_awarded']})\n"
            )
        
        await query.edit_message_text(message, parse_mode='Markdown')
    
    elif action == "stats":
        # Show stats with progress bar
        user = db.get_user(user_id)
        stats = db.get_user_stats(user_id)
        progress_bar = get_progress_bar(stats['total_tokens'], 30)
        
        message = (
            f"📊 *Your Progress*\n\n"
            f"*Name:* {user['full_name']}\n"
            f"*Matric:* {user['matric_number']}\n\n"
            f"*Tokens:* {stats['total_tokens']}/30\n"
            f"{progress_bar}\n\n"
            f"*Status:* {'✅ Starpoint Eligible!' if stats['starpoint_eligible'] else '⏳ Keep going!'}\n"
            f"*Submissions:* {stats['approved_count']} approved, {stats['pending_count']} pending, {stats['rejected_count']} rejected"
        )
        
        await query.edit_message_text(message, parse_mode='Markdown')
    
    elif action == "help":
        # Show help
        help_text = (
            "🆘 *IIUM Re:Gain Help*\n\n"
            "*Token System:*\n"
            "🔄 Reuse = +10 tokens\n"
            "♻️ Plastic (10 items) = +5 tokens\n"
            "🥫 Cans (5 items) = +5 tokens\n"
            "📄 Paper (50g) = +2 tokens\n"
            "⬇️ Reduce = +1 token\n\n"
            "*Goal:* Earn 30 tokens → Starpoint Eligible ⭐\n\n"
            "*How to Submit:*\n"
            "1. Click 📤 Submit Action\n"
            "2. Choose category\n"
            "3. Upload photo proof\n"
            "4. Wait for admin ✅"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif action == "leaderboard":
        # Show top users
        users = db.get_top_users(10)
        
        if not users:
            await query.edit_message_text("🏆 Leaderboard coming soon!")
            return
        
        message = "🏆 *Top 10 Users by Tokens*\n\n"
        for i, user in enumerate(users, 1):
            medal = ["🥇", "🥈", "🥉"]
            medal_emoji = medal[i-1] if i <= 3 else f"{i}️⃣"
            message += f"{medal_emoji} {user['full_name']} - {user['total_tokens']} tokens\n"
        
        await query.edit_message_text(message, parse_mode='Markdown')

def get_progress_bar(current: int, target: int) -> str:
    """Generate a visual progress bar"""
    filled = min(current * 10 // target, 10)
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"`{bar}` {current}/{target}"
