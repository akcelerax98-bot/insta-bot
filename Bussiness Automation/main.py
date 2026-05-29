import schedule
import time
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import database
import instagram_bot

# --- Logging Setup ---
# This logs everything to a file AND to the console so you can see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

def job():
    """Daily outreach job - runs at 9:00 AM every day."""
    log.info("⏰ Scheduled job triggered: Running daily outreach...")
    try:
        instagram_bot.run_daily_outreach()
    except Exception as e:
        log.error(f"❌ Error during daily outreach: {e}")

def run_reply_check():
    """Checks for new replies - runs every 5 minutes."""
    try:
        instagram_bot.check_for_replies()
    except Exception as e:
        log.error(f"❌ Error checking for replies: {e}")

def login_with_retry(max_attempts=5):
    """Tries to log in, retrying up to max_attempts times with delays."""
    for attempt in range(1, max_attempts + 1):
        log.info(f"Login attempt {attempt}/{max_attempts}...")
        if instagram_bot.login():
            log.info("✅ Logged in successfully.")
            return True
        wait = attempt * 60  # Wait 1 min, 2 min, 3 min, etc.
        log.warning(f"Login failed. Retrying in {wait} seconds...")
        time.sleep(wait)
    log.error("❌ All login attempts failed. Exiting.")
    return False

# --- Keep-Alive Server ---
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")
        
    def log_message(self, format, *args):
        # Suppress logging for ping requests to avoid spam
        pass

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, PingHandler)
    log.info(f"🌐 Keep-alive server running on port {port}")
    httpd.serve_forever()

def keep_alive():
    """Starts a background HTTP server to respond to ping requests."""
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

def main():
    log.info("=" * 50)
    log.info("🤖 Instagram Automation Bot Starting...")
    log.info("=" * 50)

    # Start the keep-alive server
    keep_alive()

    log.info("Initializing database...")
    database.init_db()

    if not login_with_retry():
        return

    log.info("Scheduling daily outreach at 09:00 AM...")
    schedule.every().day.at("09:00").do(job)

    log.info("✅ Bot is running 24/7. Checking replies every 5 minutes.")
    log.info("   Daily outreach is scheduled for 09:00 AM.")

    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 10  # Re-login after 10 back-to-back errors

    while True:
        try:
            # Run any scheduled jobs (9:00 AM outreach)
            schedule.run_pending()

            # Check for new replies every loop cycle
            run_reply_check()

            consecutive_errors = 0  # Reset error count on success
            time.sleep(300)  # Sleep 5 minutes

        except KeyboardInterrupt:
            log.info("🛑 Bot manually stopped.")
            break

        except Exception as e:
            consecutive_errors += 1
            log.error(f"❌ Unexpected error in main loop (#{consecutive_errors}): {e}")

            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                log.warning("⚠️  Too many errors. Attempting to re-login...")
                if login_with_retry(max_attempts=3):
                    consecutive_errors = 0
                else:
                    log.error("❌ Re-login failed. Waiting 10 minutes before retrying...")
                    time.sleep(600)
            else:
                log.info("Waiting 60 seconds before retrying...")
                time.sleep(60)

if __name__ == "__main__":
    main()
