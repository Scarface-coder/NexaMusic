from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded
from Shadow import app, OWNER_ID, API_ID, API_HASH
from Shadow.mongo import mongodb

assist_db = mongodb.assistants

# Runtime active clients
active_clients = {}

# -------- CONNECT ACCOUNT -------- #

@app.on_message(filters.command("connect") & filters.private)
async def connect_account(client, message):

    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split(" ", 1)
    if len(args) < 2:
        return await message.reply("Usage:\n/connect <string session>")

    session = args[1].strip()

    try:
        ass = Client(
            name=f"asst_{message.from_user.id}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session,
            in_memory=True
        )

        await ass.connect()
        me = await ass.get_me()

        # Save in DB
        assist_db.update_one(
            {"user_id": me.id},
            {"$set": {
                "user_id": me.id,
                "phone": me.phone_number,
                "session_string": session
            }},
            upsert=True
        )

        active_clients[me.id] = ass

        await message.reply(
            f"✅ Connected Successfully!\n\n"
            f"Assistant: <b>{me.first_name}</b>\n"
            f"UserID: <code>{me.id}</code>\n"
            f"Phone: <code>{me.phone_number}</code>"
        )

    except SessionPasswordNeeded:
        await message.reply("❌ This session requires 2FA password! Can’t login.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


# -------- DISCONNECT ACCOUNT -------- #

@app.on_message(filters.command("disconnect") & filters.private)
async def disconnect_account(client, message):

    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage:\n/disconnect <string or userid>")

    target = args[1].strip()

    # by UserID
    if target.isdigit():
        uid = int(target)
        data = assist_db.find_one({"user_id": uid})
        if not data:
            return await message.reply("❌ No assistant found with this UserID")

        # stop runtime client if active
        if uid in active_clients:
            try:
                await active_clients[uid].disconnect()
            except:
                pass
            del active_clients[uid]

        assist_db.delete_one({"user_id": uid})

        return await message.reply(f"🛑 Disconnected Assistant: <code>{uid}</code>")

    # by session string
    else:
        data = assist_db.find_one({"session_string": target})
        if not data:
            return await message.reply("❌ No assistant found with this session string")

        uid = data["user_id"]

        # stop runtime client if active
        if uid in active_clients:
            try:
                await active_clients[uid].disconnect()
            except:
                pass
            del active_clients[uid]

        assist_db.delete_one({"session_string": target})

        return await message.reply(f"🛑 Disconnected Assistant: <code>{uid}</code>")


# -------- ACCOUNT LIST -------- #

@app.on_message(filters.command(["acclist"]) & filters.private)
async def acclist(client, message):

    if message.from_user.id != OWNER_ID:
        return

    accounts = assist_db.find()
    text = "<b>📂 Connected Assistant Accounts:</b>\n\n"

    count = 0
    async for acc in accounts:
        count += 1
        text += (
            f"{count}. <b>UserID:</b> <code>{acc['user_id']}</code>\n"
            f"📱 Phone: <code>{acc.get('phone', 'N/A')}</code>\n"
            f"Session: <code>{acc['session_string'][:15]}...****</code>\n\n"
        )

    if count == 0:
        text = "No assistant accounts connected."

    await message.reply(text)