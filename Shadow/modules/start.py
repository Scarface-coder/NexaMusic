
from pyrogram import filters
from Shadow import app, OWNER_ID

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):


    if message.from_user.id != OWNER_ID:
        return

    text = (
        "<b>Welcome Owner 👑</b>\n\n"
        "<b>Your Control Commands:</b>\n"
        "• <code>/connect</code> — Add new assistant via string session\n"
        "• <code>/join <chat></code> — Send all assistants to join a chat\n"
        "• <code>/play <song/query></code> — Play audio in all VC\n"
        "• <code>/leave</code> — Make all assistants leave VC\n"
        "• <code>/status</code> — Show connected assistants + active VCs\n"
        "• <code>/addsudo</code> user_id — Add sudo\n"
        "• <code>/delsudo</code> user_id — Remove sudo\n\n"
        "<b>Everything is fully controlled by you only.</b>"
    )

    await message.reply(text)