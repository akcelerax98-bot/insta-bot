# Instagram Outreach & WhatsApp Notification Automation

This project automatically finds new e-commerce leads on Instagram, sends them an outreach message, and notifies you via WhatsApp. It also listens for replies from contacted leads and sends an auto-reply acknowledgment, immediately notifying you via WhatsApp.

## Prerequisites

1. **Python 3.8+**
2. **Instagram Account** (We recommend testing with a secondary account first).
3. **Twilio Account** for WhatsApp notifications.

## Setup Instructions

1. **Install Dependencies**
   Open your terminal in this directory and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Credentials**
   Rename `.env.example` to `.env`.
   Open the `.env` file and fill in all your credentials:
   - `INSTAGRAM_USERNAME` & `INSTAGRAM_PASSWORD`
   - `TWILIO_ACCOUNT_SID` & `TWILIO_AUTH_TOKEN` (From your Twilio console)
   - `TWILIO_WHATSAPP_NUMBER` (From Twilio, e.g., `whatsapp:+14155238886`)
   - `MY_WHATSAPP_NUMBER` (Your personal WhatsApp number, e.g., `whatsapp:+1234567890`)

3. **Twilio WhatsApp Setup**
   If you are using Twilio's WhatsApp Sandbox, you will need to send a specific join message (e.g., `join your-sandbox-word`) from your personal WhatsApp to the Twilio WhatsApp number to authorize it to send you messages.

## Running the Automation 24/7

To ensure the automation runs continuously (at exactly 9:00 AM daily and monitoring for replies every 5 minutes):

**Option 1: Run on your computer**
You can simply run the script on your computer, but your computer must stay turned on and connected to the internet 24/7.
```bash
python main.py
```

**Option 2: Run on a Virtual Private Server (VPS) - Recommended**
For true 24/7 automation without keeping your personal computer on, you should host this script on a VPS (like DigitalOcean, AWS EC2, or a Raspberry Pi).
Once on the server, you can use a process manager like `pm2` or `tmux` to keep it running in the background:

Using `tmux`:
```bash
tmux new -s instagram_bot
python main.py
# Press Ctrl+B, then D to detach. The script will keep running in the background.
```

Using `pm2`:
```bash
npm install -g pm2
pm2 start main.py --interpreter python3 --name "instagram_bot"
pm2 save
```

## How it works

1. **Database**: It automatically creates an SQLite database `outreach.db` in this folder to keep track of who was contacted and who replied. This ensures no one is messaged twice.
2. **9:00 AM Outreach**: At 9:00 AM every day, it finds 5 new e-commerce accounts using hashtags configured in `config.py`, sends them the outreach DM, logs them in the database, and sends you a WhatsApp summary.
3. **Reply Monitoring**: Every 5 minutes, it checks your recent DMs. If a previously contacted account replies (and hasn't replied before), it sends the auto-reply and notifies you immediately via WhatsApp.
