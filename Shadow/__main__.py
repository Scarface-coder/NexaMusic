import importlib
from Shadow import app, send_start_message, LOGGER
from Shadow.modules import ALL_MODULES


# ------------------------
# Ensure modules are loaded
# ------------------------
LOGGER.info("🔹 Loading Modules...")
# Explicitly ensure start_flow module is included
if "start" not in ALL_MODULES:
    ALL_MODULES.append("start")

for module_name in ALL_MODULES:
    try:
        importlib.import_module("Shadow.modules." + module_name)
        LOGGER.info(f"🥵 𝐅𝐔𝐂𝐊𝐄𝐃 💦💦: {module_name}")
    except Exception as e:
        LOGGER.error(f"❌ Failed to load module {module_name}: {e}")

LOGGER.info("𝐓𝐇𝐎𝐑𝐖𝐄𝐃 𝐒𝐄𝐌𝐄𝐍 𝐎𝐍 𝐈𝐕𝐀𝐍𝐒 𝐌𝐎𝐔𝐓𝐇 🥵💦💦💦")

# ------------------------
# Startup message
# ------------------------
send_start_message()

# ------------------------
# Start bot
# ------------------------
if __name__ == "__main__":
    LOGGER.info("𝐈𝐕𝐀𝐍 𝐒𝐄𝐑𝐕𝐈𝐂𝐄 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 🥵🌚")
    app.run()  # Pyrogram BOT_TOKEN permanent polling