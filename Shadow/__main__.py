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
        LOGGER.info(f"✅ Module loaded: {module_name}")
    except Exception as e:
        LOGGER.error(f"❌ Failed to load module {module_name}: {e}")

LOGGER.info("𝐀𝐥𝐥 Features Loaded 🥳...")

# ------------------------
# Startup message
# ------------------------
send_start_message()

# ------------------------
# Start bot
# ------------------------
if __name__ == "__main__":
    LOGGER.info("🚀 Bot Starting...")
    app.run()  # Pyrogram BOT_TOKEN permanent polling