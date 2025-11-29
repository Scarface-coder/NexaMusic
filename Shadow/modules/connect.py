from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded
from Shadow import app, OWNER_ID, API_ID, API_HASH
from Shadow.mongo import mongodb

assist_db = mongodb.assistants

# runtime active clients
active_clients = {}


# ----------- CHECK SUDO ------------ #

def is_owner(uid):
    return uid == OWNER_ID


# ----------- CONNECT ACCOUNT ------------ #

@app.on_message(filters.command("connect") & filters.private)
async def connect_account(client, message):

    if not is_owner(message.from_user.id):
        return

    args = message.text.split(" ", 1)
    if len(args) < 2:
        return await message.reply("Usage:\n/connect <string session>")

    session = args[1].strip()

    try:
        # Create assistant client
        ass = Client(
            name=f"assistant_temp",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session,
            in_memory=True
        )

        await ass.connect()
        try:
            me = await ass.get_me()
        except:
            await ass.disconnect()
            return await message.reply("❌ Invalid session string!")

        # Save DB
        assist_db.update_one(
            {"user_id": me.id},
            {
                "$set": {
                    "user_id": me.id,
                    "phone": me.phone_number,
                    "session_string": session
                }
            },
            upsert=True
        )

        # runtime store
        active_clients[me.id] = ass

        await message.reply(
            f"✅ <b>Assistant Connected!</b>\n\n"
            f"👤 Name: <b>{me.first_name}</b>\n"
            f"🆔 UserID: <code>{me.id}</code>\n"
            f"📱 Phone: <code>{me.phone_number}</code>"
        )

    except SessionPasswordNeeded:
        await message.reply("❌ This session requires 2FA password.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


# ----------- DISCONNECT ACCOUNT ------------ #

@app.on_message(filters.command("disconnect") & filters.private)
async def disconnect_account(client, message):

    if not is_owner(message.from_user.id):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("Usage:\n/disconnect <user_id | session_string>")

    target = args[1].strip()

    # Method 1: by numeric UserID
    if target.isdigit():
        uid = int(target)
        data = assist_db.find_one({"user_id": uid})
        if not data:
            return await message.reply("❌ UserID not found in assistant list.")

        # stop live session
        if uid in active_clients:
            try:
                await active_clients[uid].disconnect()
            except:
                pass
            del active_clients[uid]

        assist_db.delete_one({"user_id": uid})

        return await message.reply(f"🛑 Assistant <code>{uid}</code> disconnected.")

    # Method 2: by session string
    else:
        data = assist_db.find_one({"session_string": target})
        if not data:
            return await message.reply("❌ Session string not found in DB.")

        uid = data["user_id"]

        if uid in active_clients:
            try:
                await active_clients[uid].disconnect()
            except:
                pass
            del active_clients[uid]

        assist_db.delete_one({"session_string": target})

        return await message.reply(f"🛑 Assistant <code>{uid}</code> removed.")


# ----------- ACCOUNT LIST ------------ #

@app.on_message(filters.command("acclist") & filters.private)
async def acclist(client, message):

    if not is_owner(message.from_user.id):
        return

    accounts = assist_db.find()
    text = "<b>📂 Connected Assistants:</b>\n\n"

    count = 0
    for acc in accounts:      # FIXED: no async for
        count += 1
        text += (
            f"{count}. <b>UserID:</b> <code>{acc['user_id']}</code>\n"
            f"📱 Phone: <code>{acc.get('phone', 'N/A')}</code>\n"
            f"🔑 Session: <code>{acc['session_string'][:20]}...****</code>\n\n"
        )

    if count == 0:
        text = "❌ No assistants connected."

    await message.reply(text)