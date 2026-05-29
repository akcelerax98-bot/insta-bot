import random
import time
import os
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, LoginRequired
import config
import database
import whatsapp_notifier

cl = Client()
# Workaround for the 467 reels_tray Client Error
cl.delay_range = [1, 3]
cl.set_device({
    "app_version": "315.0.0.35.109", # Or a newer version
    "android_version": 33,
    "android_release": "13.0.0",
    "dpi": "480dpi",
    "resolution": "1080x2280",
    "manufacturer": "Samsung",
    "device": "SM-G998B",
    "model": "SM-G998B",
    "cpu": "qcom",
    "version_code": "31500035109"
})

def challenge_code_handler(username, choice):
    """Called by instagrapi when Instagram demands a verification code."""
    method = "SMS" if choice == 1 else "Email"
    print(f"\n{'='*50}")
    print(f"INSTAGRAM VERIFICATION REQUIRED for @{username}")
    print(f"Check your {method} for a code from Instagram.")
    print(f"{'='*50}")
    code = input("Enter the 6-digit verification code: ").strip()
    return code

cl.challenge_code_handler = challenge_code_handler

def login():
    if not config.INSTAGRAM_USERNAME or not config.INSTAGRAM_PASSWORD:
        print("Instagram credentials not set.")
        return False

    session_file = "session.json"

    try:
        if config.INSTAGRAM_SESSION_ID:
            print("Using provided session ID from .env...")
            cl.login_by_sessionid(config.INSTAGRAM_SESSION_ID)
            cl.dump_settings(session_file)
            print("Successfully logged into Instagram using session ID.")
            return True
            
        if os.path.exists(session_file):
            print("Loading existing session...")
            cl.load_settings(session_file)
            cl.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
            
            # Check if session is valid
            try:
                cl.get_timeline_feed()
            except Exception as e:
                print(f"Session is invalid, logging in fresh: {e}")
                cl.set_settings({})
                cl.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
        else:
            print("No saved session found. Logging in fresh (may require verification code)...")
            cl.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
            
        # Save session to avoid logging in from scratch next time
        cl.dump_settings(session_file)
        print("Successfully logged into Instagram.")
        return True

    except ChallengeRequired:
        print("\nInstagram requires a security challenge. Resolving...")
        try:
            cl.challenge_resolve(cl.last_json)
            cl.dump_settings(session_file)
            print("Challenge passed. Logged in successfully.")
            return True
        except Exception as e:
            print(f"Challenge resolution failed: {e}")
            return False

    except Exception as e:
        err = str(e)
        if "blacklist" in err.lower() or "email to help" in err.lower() or "ip" in err.lower():
            print("\n" + "="*55)
            print("INSTAGRAM BLOCKED THIS IP ADDRESS")
            print("="*55)
            print("Instagram has flagged this IP as suspicious.")
            print("\nTo fix this, do ONE of the following:")
            print("  1. Open Instagram in your browser (instagram.com)")
            print("     and log in as 'the_rare_catalyst'.")
            print("     This whitelists your IP. Then re-run the bot.")
            print("  2. Open the Instagram app on your phone and")
            print("     check for any security alerts/notifications.")
            print("  3. Wait 30-60 minutes and try again.")
            print("="*55)
        else:
            print(f"Failed to login to Instagram: {e}")
        return False

def find_new_leads():
    """
    Searches for new e-commerce leads using hashtags.
    Returns a list of dicts: {'username': '...', 'pk': '...', 'profile_url': '...'}
    """
    leads = []
    hashtag = random.choice(config.SEARCH_HASHTAGS)
    print(f"Searching for leads using hashtag: #{hashtag}")
    
    try:
        medias = cl.hashtag_medias_top(hashtag, amount=20)
        for media in medias:
            user = media.user
            username = user.username
            
            # Check if already contacted
            if not database.is_account_contacted(username):
                # Ensure it's not our own account and try to check if business
                # This check can be expanded. For simplicity we assume if they rank top in ecommerce tags they are relevant.
                leads.append({
                    'username': username,
                    'pk': user.pk,
                    'profile_url': f"https://instagram.com/{username}"
                })
            
            if len(leads) >= config.OUTREACH_LIMIT:
                break
                
    except Exception as e:
        print(f"Error finding leads: {e}")
        
    return leads

def run_daily_outreach():
    print("Starting daily outreach...")
    leads = find_new_leads()
    
    if not leads:
        print("No new leads found.")
        return
        
    contacted_accounts = []
    
    for lead in leads:
        print(f"Sending outreach to {lead['username']}...")
        try:
            # Send message
            cl.direct_send(config.OUTREACH_MESSAGE, user_ids=[lead['pk']])
            # Log in database
            database.add_contacted_account(lead['username'], lead['profile_url'], "Sent")
            contacted_accounts.append(lead)
            # Sleep to avoid rate limiting
            time.sleep(10)
        except Exception as e:
            print(f"Failed to send to {lead['username']}: {e}")
            
    if contacted_accounts:
        whatsapp_notifier.notify_daily_outreach_completed(contacted_accounts)

def check_for_replies():
    print("Checking for new replies...")
    try:
        threads = cl.direct_threads(amount=20)
        for thread in threads:
            # Check if there are messages and if the last message is from the other user
            if not thread.messages:
                continue
                
            last_message = thread.messages[0]
            if str(last_message.user_id) == str(cl.user_id):
                # We sent the last message, no new reply
                continue
                
            # The other user replied. Find out who they are.
            other_user = None
            for user in thread.users:
                if str(user.pk) == str(last_message.user_id):
                    other_user = user
                    break
                    
            if not other_user:
                continue
                
            username = other_user.username
            
            # Check if this user is in our contacted database and hasn't replied yet
            if database.is_account_contacted(username) and not database.has_replied(username):
                print(f"New reply from {username}! Sending auto-reply...")
                
                # Send auto reply
                cl.direct_send(config.AUTO_REPLY_MESSAGE, user_ids=[other_user.pk])
                
                # Mark as replied in DB
                database.mark_replied(username)
                
                # Notify via WhatsApp
                whatsapp_notifier.notify_new_reply(username, last_message.text)
                
    except Exception as e:
        print(f"Error checking replies: {e}")

if __name__ == "__main__":
    # Test script standalone
    database.init_db()
    if login():
        run_daily_outreach()
