from pyrogram import filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients  # {user_id: Client}

assist_db = mongodb.assistants
vc_db = mongodb.vc_sessions  # {user_id, chat_id}

# Cache for PyTgCalls clients
tg_clients = {}


def is_sudo(uid: int) -> bool:
    """Check if user is sudo"""
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


def get_tgc(uid: int, cli):
    """Get or create PyTgCalls client"""
    if uid not in tg_clients:
        tgc = PyTgCalls(cli)
        tgc.start()
        tg_clients[uid] = tgc
    return tg_clients[uid]


@app.on_message(filters.command("play") & filters.private)
async def play_cmd(client, message: Message):
    """Play audio by replying to MP3/voice"""
    if not is_sudo(message.from_user.id):
        return

    if not message.reply_to_message or not (
        message.reply_to_message.audio or message.reply_to_message.voice
    ):
        return await message.reply("Reply to an MP3 or Voice message with:\n/play")

    audio_msg = message.reply_to_message.audio or message.reply_to_message.voice

    # Download the file
    file_path = await audio_msg.download()

    ok = not_in_vc = err = 0

    assistants = assist_db.find()
    async for acc in assistants:
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        # Check VC session
        vc_session = await vc_db.find_one({"user_id": uid})
        if not vc_session:
            not_in_vc += 1
            continue

        chat_id = int(vc_session["chat_id"])
        cli = active_clients[uid]
        tgc = get_tgc(uid, cli)

        try:
            # Play the audio in VC
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
        msg += "\n\n⚠️ Make sure assistants have joined VC first."

    await message.reply(msg)