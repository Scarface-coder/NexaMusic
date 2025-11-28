import logging

from pyrogram import Client, filters

# ------------------------
# Telegram Bot Credentials
# ------------------------
BOT_TOKEN = "8314045999:AAFk45sqRkbIUXdK3F9t0wsKXTvub6l8zfw"
API_ID = 22657083
API_HASH = "d6186691704bd901bdab275ceaab88f3"
OWNER_ID = 8188588913

# ------------------------
# Logging setup
# ------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO,
)
LOGGER = logging.getLogger("Shadow")



# ------------------------
# Create Pyrogram Client
# ------------------------
app = Client(
    "shadow",  
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN 
)

# ------------------------
# Ping Command for Testing
# ------------------------
@app.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message):
    await message.reply_text("🏓 Pong ✅ Bot is alive!")


# ------------------------
# Startup Message
# ------------------------
def send_start_message():
    """
    Call this function after bot starts.
    Can be used to send a startup message to log group.
    """
    LOGGER.info("🚀 Bot Started!")

# ------------------------
# Optional: Dummy Application
# ------------------------
class Application:
    """
    Dummy class to mimic run_polling behavior if needed.
    Pyrogram uses app.run() instead.
    """
    @staticmethod
    def run_polling(drop_pending_updates=True):
        LOGGER.info("📡 Polling started... (drop_pending_updates=%s)" % drop_pending_updates)

# Instance
application = Application()