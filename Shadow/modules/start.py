from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb

sudo_db = mongodb.sudo


# check sudo
def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):

    uid = message.from_user.id

    # ---------- OWNER ----------
    if uid == OWNER_ID:

        text = (
            "<b>👑 Welcome Owner</b>\n\n"
            "<b>Your Control Commands:</b>\n"
            "• <code>/connect</code> — Add new assistant via string session\n"
            "• <code>/join chat_id</code> — Send all assistants to join chat\n"
            "• <code>/play</code> — Play audio in all active VC\n"
            "• <code>/leave</code> — Make all assistants leave VC\n"
            "• <code>/status</code> — Show all assistants & VC status\n"
            "• <code>/addsudo user time</code> — Add sudo user\n"
            "• <code>/rmsudo user</code> — Remove sudo user\n"
            "• <code>/sudolist</code> — List sudo users\n\n"
            "<b>You have full system control.</b>"
        )

        return await message.reply(text)

    # ---------- SUDO USER ----------
    if is_sudo(uid):

        text = (
            "<b>🛡 Welcome Sudo User</b>\n\n"
            "<b>Your Allowed Commands:</b>\n"
            "• <code>/join chat_id</code>\n"
            "• <code>/play</code>\n"
            "• <code>/leave</code>\n"
            "• <code>/status</code>\n\n"
            "<i>Note: Owner-only commands are hidden.</i>"
        )

        return await message.reply(text)

    # ---------- NORMAL USER ----------
    else:

        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💬 Contact Owner",
                        url=f"https://t.me/{(await app.get_users(OWNER_ID)).username}"
                    )
                ]
            ]
        )

        text = (
            "<b>❌ You are not authorized.</b>\n\n"
            "Please contact the owner for access."
        )

        return await message.reply(text, reply_markup=kb)