import time
from datetime import datetime, timedelta
from pyrogram import filters
from Shadow import app, OWNER_ID
from Shadow.mongo import mongodb

sudo_db = mongodb.sudo


# Convert time like: 30d, 10h, 20m → seconds
def parse_time(t):
    try:
        unit = t[-1]
        num = int(t[:-1])

        if unit == "d":
            return num * 86400
        if unit == "h":
            return num * 3600
        if unit == "m":
            return num * 60
        return None
    except:
        return None


def format_expiry(exp):
    if exp is None:
        return "PERMANENT"
    return datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M")


# Auto delete expired sudo users
async def clean_expired():
    now = int(time.time())
    expired = sudo_db.find({"expire_at": {"$lte": now, "$ne": None}})
    for x in expired:
        sudo_db.delete_one({"user_id": x["user_id"]})


@app.on_message(filters.command("addsudo") & filters.private)
async def addsudo(client, message):

    if message.from_user.id != OWNER_ID:
        return

    await clean_expired()

    args = message.text.split()

    if len(args) < 2:
        return await message.reply("Usage:\n/addsudo <user_id> <time(optional)>")

    user_id = int(args[1])
    expire_at = None

    # If time is provided
    if len(args) == 3:
        duration = parse_time(args[2])
        if duration is None:
            return await message.reply("Invalid time format! Use: 30d, 10h, 20m")
        expire_at = int(time.time()) + duration

    sudo_db.update_one(
        {"user_id": user_id},
        {"$set": {"expire_at": expire_at}},
        upsert=True
    )

    await message.reply(
        f"✅ Added to sudo:\n"
        f"UserID: <code>{user_id}</code>\n"
        f"Expiry: <b>{format_expiry(expire_at)}</b>"
    )


@app.on_message(filters.command("insudo") & filters.private)
async def insudo(client, message):

    if message.from_user.id != OWNER_ID:
        return

    await clean_expired()

    args = message.text.split()
    if len(args) != 3:
        return await message.reply("Usage:\n/insudo <user_id> <time>")

    user_id = int(args[1])
    duration = parse_time(args[2])

    if duration is None:
        return await message.reply("Invalid time format! Use: 30d, 10h, 20m")

    user = sudo_db.find_one({"user_id": user_id})
    if not user:
        return await message.reply("❌ User is not in sudo!")

    now = int(time.time())
    old_exp = user["expire_at"]

    if old_exp is None:
        return await message.reply("❌ Cannot increase time of PERMANENT sudo!")

    new_exp = old_exp + duration

    sudo_db.update_one({"user_id": user_id}, {"$set": {"expire_at": new_exp}})

    await message.reply(
        f"⏳ Time Increased!\n"
        f"UserID: <code>{user_id}</code>\n"
        f"New Expiry: <b>{format_expiry(new_exp)}</b>"
    )


@app.on_message(filters.command("rmsudo") & filters.private)
async def rmsudo(client, message):

    if message.from_user.id != OWNER_ID:
        return

    await clean_expired()

    args = message.text.split()
    if len(args) != 2:
        return await message.reply("Usage:\n/rmsudo <user_id>")

    user_id = int(args[1])

    sudo_db.delete_one({"user_id": user_id})

    await message.reply(f"❌ Removed from sudo:\nUserID: <code>{user_id}</code>")


@app.on_message(filters.command(["sudolist", "slist"]) & filters.private)
async def sudolist(client, message):

    if message.from_user.id != OWNER_ID:
        return

    await clean_expired()

    all_sudo = sudo_db.find()
    text = "<b>🛡 SUDO USERS LIST</b>\n\n"

    count = 0
    async for x in all_sudo:
        user_id = x["user_id"]
        expire = x["expire_at"]

        try:
            user = await app.get_users(user_id)
            name = user.first_name
            uname = f"@{user.username}" if user.username else "None"
        except:
            name = "Unknown"
            uname = "None"

        count += 1

        text += (
            f"<b>{count}.</b>\n"
            f"👤 <b>Name:</b> {name}\n"
            f"🆔 <b>UserID:</b> <code>{user_id}</code>\n"
            f"🔗 <b>Username:</b> {uname}\n"
            f"⏳ <b>Expires:</b> {format_expiry(expire)}\n\n"
        )

    if count == 0:
        text = "No sudo users found."

    await message.reply(text)