from pyrogram import filters
from pyrogram.errors import (
    UserAlreadyParticipant,
    InviteHashExpired,
    UserNotParticipant
)
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import GroupCallNotFound

assist_db = mongodb.assistants
vc_db = mongodb.vc_sessions     # stores which assistant is in which vc


# ================================
# SUDO CHECK
# ================================
def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


# ================================
# TG CALL CLIENTS
# ================================
tg_clients = {}

def get_tgcalls(uid, cli):
    if uid not in tg_clients:
        tg = PyTgCalls(cli)
        tg.start()
        tg_clients[uid] = tg
    return tg_clients[uid]


# ================================
# /joingc — JOIN GROUPS
# ================================
@app.on_message(filters.command("joingc") & filters.private)
async def joingc_cmd(_, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage:\n/joingc <invitelink | @username>")

    target = args[1].strip()

    ok = fail = 0

    assistants = assist_db.find()

    async for acc in assistants:       # FIXED — async for
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        try:
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
        f"📌 <b>Group Join Result</b>\n\n"
        f"🟢 Joined: <b>{ok}</b>\n"
        f"🔴 Failed: <b>{fail}</b>"
    )


# ================================
# /join — JOIN VC
# ================================
@app.on_message(filters.command("join") & filters.private)
async def join_vc_cmd(_, message):

    if not is_sudo(message.from_user.id):
        return

    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply("Usage:\n/join <chat_id | @username>")

    chat = args[1].strip()

    ok = 0
    not_in_gc = 0
    err = 0

    assistants = assist_db.find()

    async for acc in assistants:       # FIXED — async for
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        try:
            # check membership
            try:
                await cli.get_chat_member(chat, uid)
            except UserNotParticipant:
                not_in_gc += 1
                continue

            # get tgcall client
            tgc = get_tgcalls(uid, cli)

            # join vc
            await tgc.join_group_call(int(chat))
            ok += 1

            # save vc session
            vc_db.update_one(
                {"user_id": uid},
                {"$set": {"chat_id": chat}},
                upsert=True
            )

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
        msg += "\n⚠️ Use <code>/joingc</code> first."

    await message.reply(msg)


# ================================
# /leave — LEAVE VC
# ================================
@app.on_message(filters.command("leave") & filters.private)
async def leave_vc_cmd(_, message):

    if not is_sudo(message.from_user.id):
        return

    ok = 0
    err = 0

    sessions = vc_db.find()

    async for acc in sessions:       # FIXED — async for
        uid = acc["user_id"]
        chat = acc["chat_id"]

        if uid not in active_clients:
            vc_db.delete_one({"user_id": uid})
            continue

        cli = active_clients[uid]
        tgc = get_tgcalls(uid, cli)

        try:
            await tgc.leave_group_call(int(chat))
            ok += 1
            vc_db.delete_one({"user_id": uid})

        except GroupCallNotFound:
            vc_db.delete_one({"user_id": uid})

        except Exception as e:
            print(f"[VC LEAVE ERROR] {e}")
            err += 1

    await message.reply(
        f"🚪 <b>VC Leave Result</b>\n\n"
        f"🟢 Left: <b>{ok}</b>\n"
        f"🔴 Errors: <b>{err}</b>"
    )