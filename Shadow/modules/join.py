from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UserNotParticipant
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients   # {user_id: Client}

assist_db = mongodb.assistants


# -------------------- CHECK SUDO -------------------- #

def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


# -------------------- /joingc -------------------- #

@app.on_message(filters.command("joingc") & filters.private)
async def joingc_cmd(_, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(None, 1)

    if len(args) < 2:
        return await message.reply("Usage:\n/joingc <invitelink | @username>")

    target = args[1].strip()

    ok = 0
    fail = 0

    assistants = assist_db.find()   # pymongo cursor (NOT async)

    for acc in assistants:
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        try:
            if target.startswith("https://t.me/+"):
                # invite link (private)
                invite = target.split("+")[1]
                await cli.join_chat(invite)
            else:
                # public username or chat_id
                await cli.join_chat(target)

            ok += 1

        except UserAlreadyParticipant:
            ok += 1
        except InviteHashExpired:
            fail += 1
        except Exception as e:
            print(f"[JOIN GC ERROR] {e}")
            fail += 1

    await message.reply(
        f"📌 <b>Join GC Result</b>\n\n"
        f"🟢 Joined: <b>{ok}</b>\n"
        f"🔴 Failed: <b>{fail}</b>"
    )


# -------------------- /join (VC JOIN) -------------------- #

@app.on_message(filters.command("join") & filters.private)
async def join_vc_cmd(_, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(None, 1)

    if len(args) < 2:
        return await message.reply("Usage:\n/join <chat_id | @username | invite>")

    chat = args[1].strip()

    ok = 0
    not_in_gc = 0
    err = 0

    assistants = assist_db.find()

    for acc in assistants:
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        try:
            # check if bot is in group
            try:
                await cli.get_chat_member(chat, uid)
            except UserNotParticipant:
                not_in_gc += 1
                continue

            # join vc
            await cli.join_call(chat)
            ok += 1

        except Exception as e:
            print(f"[VC JOIN ERROR] {e}")
            err += 1

    msg = (
        f"🎧 <b>VC Join Result</b>\n\n"
        f"🟢 VC Joined: <b>{ok}</b>\n"
        f"🟡 Not in Group: <b>{not_in_gc}</b>\n"
        f"🔴 Errors: <b>{err}</b>"
    )

    if not_in_gc > 0:
        msg += "\n\n⚠️ First use <code>/joingc</code> to add assistants in this chat."

    await message.reply(msg)