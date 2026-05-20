"""
Export eligible users to CSV
"""
import csv
import io
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database.db import Database
from config import ADMIN_IDS

db = Database()

async def export_eligible(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export eligible users to CSV file"""
    user_id = update.effective_user.id
    
    if str(user_id) not in ADMIN_IDS:
        await update.message.reply_text("❌ You don't have admin access.")
        return
    
    eligible = db.get_eligible_users()
    
    if not eligible:
        await update.message.reply_text("📊 No eligible users to export!")
        return
    
    # Create CSV in memory
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=['User ID', 'Matric Number', 'Full Name', 'Total Tokens', 'Date Eligible'])
    
    writer.writeheader()
    for user in eligible:
        writer.writerow({
            'User ID': user['user_id'],
            'Matric Number': user['matric_number'],
            'Full Name': user['full_name'],
            'Total Tokens': user['total_tokens'],
            'Date Eligible': user['created_at']
        })
    
    # Get CSV content as bytes
    csv_content = csv_buffer.getvalue()
    csv_bytes = csv_content.encode('utf-8')
    
    # Create filename with timestamp
    filename = f"eligible_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Send file to admin
    await context.bot.send_document(
        chat_id=user_id,
        document=csv_bytes,
        filename=filename,
        caption=f"✅ Exported {len(eligible)} eligible users"
    )
    
    await update.message.reply_text(f"✅ CSV file exported successfully!\nTotal users: {len(eligible)}")
