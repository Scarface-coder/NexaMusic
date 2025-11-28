from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UserNotParticipant
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db   # sudo list from your sudo module
from .connect import active_clients  # active assistant clients

assist_db = mongodb.assistants


# Check if user is sudo or owner
def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


# -------------------- /joingc -------------------- #

@app.on_message(filters.command("joingc") & filters.private)
async def joingc_cmd(client, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage:\n/joingc <invitelink | @username>")

    target = args[1].strip()

    ok = 0
    fail = 0

    # fetch all assistant accounts
    assistants = assist_db.find()

    async for acc in assistants:
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        try:
            if target.startswith("https://t.me/+"):
                # Invite link join
                invite = target.split("+")[1]
                await cli.join_chat(invite)

            else:
                # Username or public chat
                await cli.join_chat(target)

            ok += 1

        except UserAlreadyParticipant:
            ok += 1
        except InviteHashExpired:
            fail += 1
        except Exception:
            fail += 1

    await message.reply(
        f"📌 <b>Join GC Result</b>\n\n"
        f"🟢 Joined: <b>{ok}</b>\n"
        f"🔴 Failed: <b>{fail}</b>"
    )


# -------------------- /join (VC join) -------------------- #

@app.on_message(filters.command("join") & filters.private)
async def join_vc_cmd(client, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage:\n/join <chat_id | @username | invite>")

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
            # Check if assistant already in chat
            try:
                await cli.get_chat_member(chat, uid)
            except UserNotParticipant:
                not_in_gc += 1
                continue

            # joining voice chat
            await cli.join_voice_chat(chat)
            ok += 1

        except Exception:
            err += 1

    msg = (
        f"🎧 <b>VC Join Result</b>\n\n"
        f"🟢 VC Joined: <b>{ok}</b>\n"
        f"🟡 Not in Group: <b>{not_in_gc}</b>\n"
        f"🔴 Errors: <b>{err}</b>"
    )

    if not_in_gc > 0:
        msg += "\n\n⚠️ First use <code>/joingc</code> to add accounts in this chat."

    await message.reply(msg)