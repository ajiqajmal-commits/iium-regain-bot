# IIUM Re:Gain Telegram Bot 🌱

A gamified 3R (Recycle, Reuse, Reduce) initiative for IIUM students to earn Starpoints through sustainable practices.

## Features

✅ **User Registration** - Matric number verification  
✅ **Action Submission** - Photo-based evidence upload  
✅ **Token System** - Earn tokens through recycling/reusing/reducing  
✅ **Admin Panel** - Verify and approve submissions  
✅ **Progress Tracking** - Real-time token count and Starpoint eligibility  
✅ **Database** - SQLite for persistent storage  

## Token System

| Action | Tokens | Details |
|--------|--------|---------|
| 🔄 Reuse | +10 | Using personal containers/bags |
| ♻️ Recycle Plastics | +5 | 10 plastic items |
| 🥫 Recycle Cans | +5 | 5 tins/cans |
| 📄 Recycle Paper | +2 | 50g of paper |
| ⬇️ Reduce | +1 | Opting out of plastic cutlery |

**Goal:** Earn 30 tokens → Eligibility for Starpoints ⭐

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- pip (Python package manager)

### 2. Installation

```bash
# Clone or download the project
cd regain-telegram-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Create a `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```

2. Get your Telegram Bot Token:
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the token

3. Update `.env` file:
```
BOT_TOKEN=your_token_here
ADMIN_IDS=your_user_id,other_admin_id
```

4. Get your user ID:
   - Run the bot
   - Send any message to it
   - Check the terminal logs for `user_id`

### 4. Run the Bot

```bash
python main.py
```

You should see:
```
✅ Bot started! Polling for updates...
```

## Usage

### For Students

1. Start the bot: `/start`
2. Register with your matric number
3. Submit actions with photos
4. Track progress: `/mystats`
5. Learn more: `/help`

### For Admins

1. Send `/admin` to access the admin panel
2. View pending submissions
3. Verify photos and approve/reject
4. Check statistics: `/admin`

## Project Structure

```
regain-telegram-bot/
├── main.py                 # Main bot entry point
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── database/
│   ├── models.py         # Data models
│   └── db.py            # Database operations
├── handlers/
│   ├── start.py         # /start, /help, /mystats commands
│   ├── register.py      # Registration flow
│   └── submit.py        # Action submission flow
├── admin/
│   └── panel.py         # Admin verification panel
└── README.md
```

## Database

The bot uses SQLite with three main tables:

- **users** - Student profiles and token counts
- **submissions** - Action submissions and verification status
- **verifications** - Admin verification records

Database file: `regain_bot.db`

## Commands

| Command | Description |
|---------|------------|
| `/start` | Start bot and show main menu |
| `/help` | Show help and token system info |
| `/mystats` | View your progress |
| `/admin` | Access admin panel (admins only) |
| `/cancel` | Cancel current operation |

## Troubleshooting

### Bot not responding
- Check if `BOT_TOKEN` is correctly set in `.env`
- Verify the token is valid (no typos)
- Ensure the bot has been started: `python main.py`

### Database errors
- Delete `regain_bot.db` and restart (fresh database)
- Check file permissions in the directory

### Admin access denied
- Add your user ID to `ADMIN_IDS` in `.env`
- Restart the bot after changing

## Future Enhancements

- 🎯 Leaderboard system
- 📊 Analytics dashboard
- 🔔 Push notifications
- 💾 Backup functionality
- 🌍 Multi-language support

## License

Educational project for IIUM Engineering Ethics Course

## Contact

For issues or suggestions, contact the project team.

---

**Let's make IIUM Green! ♻️🌱**
