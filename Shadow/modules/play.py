from pyrogram import filters
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients
from .join import assistant_vc   # {assistant_user_id: chat_id}

assist_db = mongodb.assistants


# Sudo check
def is_sudo(uid):
    if uid == OWNER_ID:
        return True
    return sudo_db.find_one({"user_id": uid}) is not None


@app.on_message(filters.command("play") & filters.private)
async def play_cmd(client, message):

    if not is_sudo(message.from_user.id):
        return

    if not message.reply_to_message or not message.reply_to_message.audio:
        return await message.reply("Reply to an audio file with:\n/play")

    audio = message.reply_to_message.audio

    # download audio to temp file
    file_path = await message.reply_to_message.download()

    ok = 0
    not_in_vc = 0
    err = 0

    assistants = assist_db.find()

    for acc in assistants:     # FIXED - No async for
        uid = acc["user_id"]

        if uid not in active_clients:
            continue

        cli = active_clients[uid]

        # assistant must be in VC
        if uid not in assistant_vc:
            not_in_vc += 1
            continue

        chat_id = assistant_vc[uid]

        try:
            # play/stream audio in VC
            await cli.change_stream(
                chat_id,
                file_path,
                video=False,          # audio only
                audio=True
            )

            ok += 1

        except Exception as e:
            print(f"[PLAY ERROR] {e}")
            err += 1

    msg = (
        f"🎵 <b>PLAY RESULT</b>\n\n"
        f"🟢 Playing in VC: <b>{ok}</b>\n"
        f"🟡 Not in VC: <b>{not_in_vc}</b>\n"
        f"🔴 Errors: <b>{err}</b>"
    )

    if not_in_vc > 0:
        msg += "\n\n⚠️ Use <code>/join</code> first to join VC."

    await message.reply(msg)