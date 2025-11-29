from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb
from .sudo import sudo_db
from .connect import active_clients  # {user_id: Client}

@app.on_message(filters.command("play") & filters.private)
async def play_multi(client, message):
    user_id = message.from_user.id

    # Fetch sudo users
    sudo_users = await sudo_db.find().to_list(None)
    sudo_list = [x["user_id"] for x in sudo_users]

    # Also owner is sudo
    sudo_list.append(OWNER_ID)

    # Check permission
    if user_id not in sudo_list:
        return await message.reply("❌ Only sudo users can use multi-play command.")

    # Your play logic
    args = message.text.split()
    if len(args) < 2 and not message.reply_to_message:
        return await message.reply("Usage: /play <chat_id> or reply to an mp3")

    target_chat = None

    if message.reply_to_message:
        target_chat = args[1] if len(args) > 1 else None
    else:
        target_chat = args[1]

    try:
        target_chat = int(target_chat)
    except:
        return await message.reply("Invalid chat ID!")

    # Connect the assistant account
    if user_id not in active_clients:
        return await message.reply("❌ You are not connected with assistant!")

    client_acc = active_clients[user_id]

    # Join VC
    try:
        await client_acc.join_chat(target_chat)
    except Exception as e:
        return await message.reply(f"Join error: {e}")

    # Play audio
    if message.reply_to_message and message.reply_to_message.audio:
        audio = message.reply_to_message.audio.file_id
        await client_acc.send_audio(target_chat, audio)
        return await message.reply("▶️ Playing audio in target chat!")

    return await message.reply("Done!")