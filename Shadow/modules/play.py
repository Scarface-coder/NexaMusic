import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream

from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients   # {user_id: Client}


# ============================
#  /play <chat_id> (reply to mp3)
# ============================
@app.on_message(filters.command("play") & filters.private)
async def play_multi(_, message: Message):

    # check sudo
    user_id = message.from_user.id
    if user_id not in sudo_db():
        return await message.reply("⛔ Only SUDO users can use this.")

    # check reply audio
    if not message.reply_to_message or not message.reply_to_message.audio:
        return await message.reply("Reply to an audio file.\nUsage:\n`/play -100123456789`")

    audio = message.reply_to_message.audio

    # check argument
    try:
        chat_id = int(message.text.split()[1])
    except:
        return await message.reply("❌ Please give valid chat id.\n\nExample: `/play -10083837382`")

    # check active userbot client
    if user_id not in active_clients:
        return await message.reply(
            "⚠️ Your assistant account is not connected.\n\nUse: `/connect` first."
        )

    userbot = active_clients[user_id]
    call = PyTgCalls(userbot)

    # START
    status = await message.reply("➡ Downloading audio...")

    # download file
    file_path = await userbot.download_media(audio)

    await status.edit("➡ Joining VC...")

    # join the VC
    try:
        await call.join_group_call(
            chat_id,
            InputAudioStream(file_path)
        )
    except Exception as e:
        return await status.edit(f"❌ VC Join Error:\n{e}")

    await status.edit(
        f"✅ **Playing Audio**\n\n"
        f"Chat: `{chat_id}`\n"
        f"Userbot: `{userbot.me.first_name}`"
    )