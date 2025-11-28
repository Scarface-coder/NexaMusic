import os
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from pyrogram import Client
from Shadow import BOT_TOKEN, API_ID, API_HASH 

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://NexaMusic_db_user:NexaMusic@cluster0.prxrqda.mongodb.net/?appName=Cluster0").strip()

from Shadow import LOGGER

TEMP_MONGODB = ""


if MONGO_URI is None:
    LOGGER(__name__).warning("No MONGO DB URL found. LOL")
    temp_client = Client(
        "Sha",
        bot_token=BOT_TOKEN,
        api_id=API_ID,
        api_hash=API_HASH,
    )
    temp_client.start()
    info = temp_client.get_me()
    username = info.username
    temp_client.stop()
    _mongo_async_ = _mongo_client_(TEMP_MONGODB)
    _mongo_sync_ = MongoClient(TEMP_MONGODB)
    mongodb = _mongo_async_[username]
    pymongodb = _mongo_sync_[username]
else:
    _mongo_async_ = _mongo_client_(MONGO_URI)
    _mongo_sync_ = MongoClient(MONGO_URI)
    mongodb = _mongo_async_.Sha
    pymongodb = _mongo_sync_.Sha