"""
Admin verification panel
"""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database.db import Database
from config import ADMIN_IDS

db = Database()

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ You don't have admin access.")
        return
    
    await show_pending_submissions(update, context)

async def show_pending_submissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending submissions for verification"""
    submissions = db.get_pending_submissions()
    
    if not submissions:
        await update.message.reply_text("✅ No pending submissions!")
        return
    
    message_text = f"📋 *Pending Submissions: {len(submissions)}*\n\n"
    
    for sub in submissions[:10]:  # Show first 10
        emoji_map = {
            'reuse': '🔄',
            'recycle_plastics': '♻️',
            'recycle_cans': '🥫',
            'recycle_paper': '📄',
            'reduce': '⬇️'
        }
        emoji = emoji_map.get(sub['category'], '📌')
        
        message_text += (
            f"ID: #{sub['submission_id']}\n"
            f"User: {sub['full_name']} ({sub['matric_number']})\n"
            f"Action: {emoji} {sub['category']}\n"
            f"Tokens: +{sub['tokens_awarded']}\n"
            f"Date: {sub['created_at']}\n\n"
        )
    
    # Show first submission for verification
    if submissions:
        first_sub = submissions[0]
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{first_sub['submission_id']}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{first_sub['submission_id']}")
            ],
            [
                InlineKeyboardButton("📸 View Photo", callback_data=f"view_photo_{first_sub['submission_id']}")
            ]
        ])
        
        await update.message.reply_text(message_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(message_text)

async def view_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View submission photo"""
    query = update.callback_query
    await query.answer()
    
    submission_id = int(query.data.split('_')[2])
    submission = db.get_submission(submission_id)
    
    if submission:
        await context.bot.send_photo(
            chat_id=query.from_user.id,
            photo=submission['photo_file_id'],
            caption=f"Submission #{submission_id}"
        )
        
        # Show approval/rejection buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{submission_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{submission_id}")
            ]
        ])
        
        await query.edit_message_reply_markup(reply_markup=keyboard)

async def approve_submission_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a submission"""
    query = update.callback_query
    await query.answer()
    
    admin_id = query.from_user.id
    submission_id = int(query.data.split('_')[1])
    
    submission = db.get_submission(submission_id)
    if not submission:
        await query.edit_message_text("❌ Submission not found!")
        return
    
    if db.approve_submission(submission_id, admin_id):
        user = db.get_user(submission['user_id'])
        tokens = submission['tokens_awarded']
        
        # Notify user
        await context.bot.send_message(
            chat_id=submission['user_id'],
            text=f"✅ *Submission Approved!*\n\n"
                 f"You earned *+{tokens} tokens*! 🎉\n"
                 f"Check /mystats for your progress.",
            parse_mode='Markdown'
        )
        
        await query.edit_message_text(
            f"✅ Submission #{submission_id} approved!\n"
            f"User {user['full_name']} earned +{tokens} tokens."
        )
        
        # Show next submission
        await show_pending_submissions(update.effective_chat, context)
    else:
        await query.edit_message_text("❌ Error approving submission.")

async def reject_submission_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a submission - ask for reason"""
    query = update.callback_query
    await query.answer()
    
    submission_id = int(query.data.split('_')[1])
    admin_id = query.from_user.id
    
    submission = db.get_submission(submission_id)
    if not submission:
        await query.edit_message_text("❌ Submission not found!")
        return
    
    # Store rejection context
    context.user_data['rejecting_submission_id'] = submission_id
    context.user_data['admin_id'] = admin_id
    
    # Add buttons for skip or provide reason
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏭️ Skip Reason", callback_data=f"skip_reason_{submission_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_reject")
        ]
    ])
    
    await query.edit_message_text(
        "Provide a rejection reason (optional) or skip:\n\n"
        "Reply with your reason or click Skip Reason below.",
        reply_markup=keyboard
    )
    
    # Set state to await reason
    context.user_data['awaiting_reject_reason'] = True

async def skip_reason_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip rejection reason and reject without reason"""
    query = update.callback_query
    await query.answer()
    
    submission_id = int(query.data.split('_')[2])
    admin_id = query.from_user.id
    
    if db.reject_submission(submission_id, admin_id, reason=None):
        await query.edit_message_text("✅ Submission rejected (no reason provided)")
        
        # Notify user
        submission = db.get_submission(submission_id)
        await context.bot.send_message(
            chat_id=submission['user_id'],
            text=f"❌ *Submission Rejected*\n\n"
                 f"Submission ID: #{submission_id}\n"
                 f"Reason: Not specified\n\n"
                 f"You can try again!",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❌ Error rejecting submission")
    
    context.user_data.clear()

async def cancel_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel rejection"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Rejection cancelled")
    context.user_data.clear()

async def handle_rejection_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text message with rejection reason"""
    if not context.user_data.get('awaiting_reject_reason'):
        return
    
    reason_text = update.message.text
    submission_id = context.user_data.get('rejecting_submission_id')
    admin_id = context.user_data.get('admin_id')
    
    if not submission_id:
        await update.message.reply_text("❌ Error: submission not found")
        return
    
    # Reject with reason
    if db.reject_submission(submission_id, admin_id, reason=reason_text):
        await update.message.reply_text(
            f"✅ Submission #{submission_id} rejected with reason:\n"
            f'"{reason_text}"'
        )
        
        # Notify user
        submission = db.get_submission(submission_id)
        await context.bot.send_message(
            chat_id=submission['user_id'],
            text=f"❌ *Submission Rejected*\n\n"
                 f"Submission ID: #{submission_id}\n"
                 f"Reason: {reason_text}\n\n"
                 f"You can try again!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Error rejecting submission")
    
    context.user_data.clear()

async def verify_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show verification statistics"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ You don't have admin access.")
        return
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as total FROM submissions WHERE status = "pending"')
    pending = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM submissions WHERE status = "approved"')
    approved = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM submissions WHERE status = "rejected"')
    rejected = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM users WHERE starpoint_eligible = 1')
    eligible = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM users')
    total_users = cursor.fetchone()['total']
    
    conn.close()
    
    stats_text = (
        f"📊 *Admin Statistics*\n\n"
        f"*Submissions:*\n"
        f"⏳ Pending: {pending}\n"
        f"✅ Approved: {approved}\n"
        f"❌ Rejected: {rejected}\n\n"
        f"*Users:*\n"
        f"👥 Total Registered: {total_users}\n"
        f"⭐ Starpoint Eligible: {eligible}\n"
    )
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')
