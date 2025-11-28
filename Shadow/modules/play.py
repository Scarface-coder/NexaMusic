from pyrogram import filters
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients
from .join import assistant_vc   # vc session map

assist_db = mongodb.assistants


# check sudo
def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


@app.on_message(filters.command("play"))
async def play_cmd(client, message):

    if not is_sudo(message.from_user.id):
        return

    # must reply to an audio
    if not message.reply_to_message or not message.reply_to_message.audio:
        return await message.reply("Reply to an MP3 file with:\n/play")

    audio = message.reply_to_message.audio

    # download audio file
    file_path = await message.reply_to_message.download()

    ok = 0
    not_in_vc = 0
    err = 0

    assistants = assist_db.find()

    async for acc in assistants:
        uid = acc["user_id"]

        # assistant must be active
        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        # assistant MUST be in VC somewhere
        if uid not in assistant_vc:
            not_in_vc += 1
            continue

        chat_id = assistant_vc[uid]

        try:
            # play audio in VC
            await cli.join_voice_chat(
                chat_id,
                file_path,
                stream_type="local_stream"
            )

            ok += 1

        except Exception as e:
            err += 1

    msg = (
        f"🎵 <b>PLAY RESULT</b>\n\n"
        f"🟢 Playing in VC: <b>{ok}</b>\n"
        f"🟡 Not in VC: <b>{not_in_vc}</b>\n"
        f"🔴 Errors: <b>{err}</b>"
    )

    if not_in_vc > 0:
        msg += "\n\n⚠️ Use <code>/join</code> first."

    await message.reply(msg)