# ------------------------- #
# Don't Remove Credit 
# Ask Doubt @AU_Bot_Discussion 
# Owner @Mr_Mohammed_29 
# ------------------------- #

from pyrogram import Client, filters
import time
import os

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from keep_alive import keep_alive

from start import start_handler
from sticker import ask_sticker, handle_sticker
from callback import callback_handler
from database import add_user, get_stats, get_all_users
from utils import START_TIME, VERSION

from pymongo import MongoClient
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= MONGO =================

MONGO_URL = os.environ.get("MONGO_URL")
mongo = MongoClient(MONGO_URL)
db = mongo["StickerBot"]
fsub_col = db["force_sub"]

# ================= BOT =================

bot = Client(
    "StickerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

broadcast_mode = set()

# ================= FORCE SUB =================

def get_fsubs():
    data = fsub_col.find_one({"_id": "fsubs"})
    return data.get("channels", []) if data else []

def add_fsub(channel):
    fsub_col.update_one(
        {"_id": "fsubs"},
        {"$addToSet": {"channels": channel}},
        upsert=True
    )

def remove_fsub(channel):
    fsub_col.update_one(
        {"_id": "fsubs"},
        {"$pull": {"channels": channel}}
    )

async def check_force_sub(client, user_id):

    if user_id == OWNER_ID:
        return True

    channels = get_fsubs()
    if not channels:
        return True

    for channel in channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]:
                return False
        except:
            return False

    return True


# ================= FORCE SUB CHECKER =================

@bot.on_message(filters.private & ~filters.command([
    "start", "stickerid", "stats", "broadcast",
    "fsub", "nofsub", "listfsub"
]))
async def force_sub_checker(client, message):

    if not message.from_user:
        return

    channels = get_fsubs()
    if not channels:
        return

    ok = await check_force_sub(client, message.from_user.id)

    if ok:
        return

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📢 Join Channel",
            url=f"https://t.me/{channels[0].replace('@','')}"
        )]
    ])

    await message.reply_text(
        "❌ Join our channel to use this bot.",
        reply_markup=btn
    )


# ================= COMMANDS =================

@bot.on_message(filters.command("start"))
async def start(_, msg):
    add_user(msg.from_user.id)
    await start_handler(bot, msg)


@bot.on_message(filters.command("stickerid"))
async def ask(_, msg):
    add_user(msg.from_user.id)
    await ask_sticker(bot, msg)


@bot.on_message(filters.sticker)
async def sticker(_, msg):
    add_user(msg.from_user.id)
    await handle_sticker(bot, msg)


# ================= STATS =================

@bot.on_message(filters.command("stats"))
async def stats(_, msg):

    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("Yᴏᴜ Aʀᴇ Nᴏᴛ Mʏ Mᴀsᴛᴇʀ.")

    start_ping = time.time()
    users, stickers = get_stats()
    ping = round((time.time() - start_ping) * 1000, 2)

    uptime_sec = int(time.time() - START_TIME)

    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    minutes = (uptime_sec % 3600) // 60
    seconds = uptime_sec % 60

    uptime = f"{days}d {hours}h {minutes}m {seconds}s"

    await msg.reply_text(f"""
📊 𝗕𝗼𝘁 𝗦𝘁𝗮𝘁𝘀

👥 Users: {users}
🎯 Stickers: {stickers}
⚡ Ping: {ping} ms
⏱ Uptime: {uptime}
🧬 Version: {VERSION}
""")


# ================= BROADCAST =================

@bot.on_message(filters.command("broadcast"))
async def broadcast(_, msg):

    if msg.from_user.id != OWNER_ID:
        return await msg.reply_text("Not allowed")

    broadcast_mode.add(msg.from_user.id)
    await msg.reply_text("Send message to broadcast")


@bot.on_message(filters.private & filters.text & ~filters.command([
    "start","stats","stickerid","fsub","nofsub","listfsub","broadcast"
]))
async def send_broadcast(_, msg):

    if msg.from_user.id not in broadcast_mode:
        return

    users = get_all_users()

    ok, fail = 0, 0

    for u in users:
        try:
            await bot.send_message(u[0], msg.text)
            ok += 1
        except:
            fail += 1

    await msg.reply_text(f"Done\nSent: {ok}\nFailed: {fail}")

    broadcast_mode.remove(msg.from_user.id)


# ================= CALLBACK =================

@bot.on_callback_query()
async def cb(_, q):
    await callback_handler(bot, q)


# ================= SAVE USER =================

@bot.on_message(filters.private & ~filters.command([
    "start","stats","stickerid","fsub","nofsub","listfsub","broadcast"
]))
async def save_user(_, msg):

    if not msg.from_user:
        return

    try:
        add_user(msg.from_user.id)
    except:
        pass


# ================= START BOT =================

if __name__ == "__main__":
    keep_alive()
    print("Bot Running...")
    bot.run()
