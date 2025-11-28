from pyrogram import filters
from pyrogram.errors import UserNotParticipant
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients

assist_db = mongodb.assistants


# Check sudo OR owner
def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


# ---------------------- LEAVE VC ---------------------- #

@app.on_message(filters.command("leave") & filters.private)
async def leave_vc_cmd(client, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage:\n/leave <chat_id | invite link | @username>")

    chat = args[1].strip()

    ok = 0
    not_in_gc = 0
    err = 0

    assistants = assist_db.find()

    async for acc in assistants:
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        try:
            # Check if assistant is present in the chat
            try:
                await cli.get_chat_member(chat, uid)
            except UserNotParticipant:
                not_in_gc += 1
                continue

            # Leave VC
            await cli.leave_voice_chat(chat)
            ok += 1

        except Exception:
            err += 1

    msg = (
        f"🎧 <b>VC Leave Result</b>\n\n"
        f"🟢 VC Left: <b>{ok}</b>\n"
        f"🟡 Not in Group: <b>{not_in_gc}</b>\n"
        f"🔴 Errors: <b>{err}</b>"
    )

    await message.reply(msg)



# ---------------------- LEAVE GROUP CHAT ---------------------- #

@app.on_message(filters.command("leavegc") & filters.private)
async def leave_gc_cmd(client, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage:\n/leavegc <chat_id | @username | invite>")

    chat = args[1].strip()

    ok = 0
    fail = 0

    assistants = assist_db.find()

    async for acc in assistants:
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        try:
            # If present → leave group
            try:
                await cli.get_chat_member(chat, uid)
            except UserNotParticipant:
                fail += 1
                continue

            await cli.leave_chat(chat)
            ok += 1

        except Exception:
            fail += 1

    await message.reply(
        f"📤 <b>Group Leave Result</b>\n\n"
        f"🟢 Left: <b>{ok}</b>\n"
        f"🔴 Failed: <b>{fail}</b>"
    )