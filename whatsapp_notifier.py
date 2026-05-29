from twilio.rest import Client
import config
import datetime

def get_twilio_client():
    if not config.TWILIO_ACCOUNT_SID or not config.TWILIO_AUTH_TOKEN:
        print("Twilio credentials not configured. Skipping WhatsApp notification.")
        return None
    return Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(body):
    client = get_twilio_client()
    if not client:
        return
    
    if not config.MY_WHATSAPP_NUMBERS or not config.TWILIO_WHATSAPP_NUMBER:
        print("WhatsApp numbers not configured.")
        return

    for number in config.MY_WHATSAPP_NUMBERS:
        try:
            message = client.messages.create(
                body=body,
                from_=config.TWILIO_WHATSAPP_NUMBER,
                to=number
            )
            print(f"WhatsApp notification sent to {number}: {message.sid}")
        except Exception as e:
            print(f"Failed to send WhatsApp message to {number}: {e}")

def notify_daily_outreach_completed(accounts):
    """
    accounts is a list of dictionaries with 'username'
    """
    date_str = datetime.datetime.now().strftime("%d/%m/%Y")
    
    body = f"✅ Daily Instagram Outreach Completed\n\n"
    body += f"📅 Date: {date_str}\n"
    body += f"⏰ Time: 09:00 AM\n\n"
    body += "Today's Outreach Accounts:\n\n"
    
    for i, acc in enumerate(accounts, 1):
        body += f"{i}. @{acc['username']}\n"
        
    body += f"\n📊 Total Messages Sent: {len(accounts)}\n\n"
    body += "All outreach messages have been sent successfully."
    
    send_whatsapp_message(body)

def notify_new_reply(username, message_text):
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    
    body = "🚨 New Lead Reply Received\n\n"
    body += f"👤 Instagram: @{username}\n\n"
    body += f"💬 Customer Message:\n\"{message_text}\"\n\n"
    body += f"🔗 Profile:\nhttps://instagram.com/{username}\n\n"
    body += f"⏰ Time:\n{time_str}\n\n"
    body += "Action Required:\nPlease continue the conversation manually on Instagram."
    
    send_whatsapp_message(body)
