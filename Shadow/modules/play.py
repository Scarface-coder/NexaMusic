from pyrogram import filters
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients     # {user_id: Client}
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

assist_db = mongodb.assistants
vc_db = mongodb.vc_sessions            # {user_id, chat_id}

# PyTgCalls client cache
tg_clients = {}


def get_tgc(uid, cli):
    if uid not in tg_clients:
        tgc = PyTgCalls(cli)
        tgc.start()
        tg_clients[uid] = tgc
    return tg_clients[uid]


# Sudo check
def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


# =========================
#       /play
# =========================
@app.on_message(filters.command("play") & filters.private)
async def play_cmd(client, message):

    if not is_sudo(message.from_user.id):
        return

    if not message.reply_to_message or not message.reply_to_message.audio:
        return await message.reply("Reply to an audio with:\n/play")

    # Download audio file
    file_path = await message.reply_to_message.download()

    ok = 0
    not_in_vc = 0
    err = 0

    assistants = assist_db.find()

    async for acc in assistants:       # FIXED async iteration
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        # Check VC session from DB
        vc_session = await vc_db.find_one({"user_id": uid})
        if not vc_session:
            not_in_vc += 1
            continue

        chat_id = int(vc_session["chat_id"])
        cli = active_clients[uid]
        tgc = get_tgc(uid, cli)

        try:
            # Play in VC
            await tgc.change_stream(
                chat_id,
                AudioPiped(file_path)
            )
            ok += 1

        except Exception as e:
            print(f"[PLAY ERROR] {e}")
            err += 1

    msg = (
        f"🎵 <b>Play Result</b>\n\n"
        f"🟢 Streaming in VC: <b>{ok}</b>\n"
        f"🟡 Not in VC: <b>{not_in_vc}</b>\n"
        f"🔴 Errors: <b>{err}</b>"
    )

    if not_in_vc > 0:
        msg += "\n\n⚠️ Use <code>/join</code> first."

    await message.reply(msg)