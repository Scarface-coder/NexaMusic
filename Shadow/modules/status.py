from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from pyrogram import filters


# Helper → check sudo or owner
async def is_auth(msg):
    user = msg.from_user.id
    if user == OWNER_ID:
        return True
    sudo = await mongodb.sudo.get_sudo_users()
    return user in sudo


@app.on_message(filters.command("status"))
async def status_command(client, message):

    # authorization check
    if not await is_auth(message):
        return

    # fetch accounts
    accounts = await mongodb.accounts.get_all_accounts()
    if not accounts:
        return await message.reply("❌ <b>No accounts connected.</b>")

    text = "<b>📊 Active Accounts Status</b>\n\n"

    for acc in accounts:
        user_id = acc.get("user_id")
        name = acc.get("name", "Unknown")
        username = acc.get("username", None)

        text += f"👤 <b>{name}</b> (<code>{user_id}</code>)\n"
        if username:
            text += f"🧩 Username: @{username}\n"
        else:
            text += f"🧩 Username: <i>Not Available</i>\n"

        # Fetch VC joining info
        vc_chats = await mongodb.vc.get_account_vc(user_id)

        if not vc_chats:
            text += "🎧 VC: <b>Not in any VC</b>\n"
        else:
            text += "🎧 <b>VC Chats:</b>\n"
            for chat in vc_chats:
                cid = chat.get("chat_id")
                cname = chat.get("chat_name", "Unknown Chat")

                text += f"   • {cname} (<code>{cid}</code>)\n"

        text += "\n"  # space for next account

    await message.reply(text)