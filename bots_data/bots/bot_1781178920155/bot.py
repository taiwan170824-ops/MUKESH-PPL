import telebot
import requests
import pytz
import time

# ================= CONFIG =================
BOT_TOKEN = "8742897760:AAGx9QOtXL7MJ2cIAPUtMmXSXGx6c3VWk-s"  # ⚠️ Token BotFather se regenerate karke yaha daalo

OWNER_NAME = "@AG Contact or buy autolike source code"
API_URL = "https://mukesh-ult-like.vercel.app/like?uid={uid}&region=ind&key=UDIT"
IST = pytz.timezone("Asia/Kolkata")

COOLDOWN = 20  # seconds per user
user_last_used = {}
# =========================================

bot = telebot.TeleBot(BOT_TOKEN)

# ================= FONT =================
def sc(text):
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    small = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789"
    return text.translate(str.maketrans(normal, small))

def footer():
    return sc(f"\n\n━━━━━━━━━━━━━━\n👑 owner : {OWNER_NAME}")

# ================= API CALL =================
def call_api(uid):
    try:
        r = requests.get(API_URL.format(uid=uid), timeout=30)
        data = r.json()

        if "LikesbeforeCommand" not in data or "LikesafterCommand" not in data:
            return None, data.get("message", "api error")

        if data.get("remaining", 1) <= 0:
            return None, "❌ daily limit over"

        return data, None

    except requests.exceptions.Timeout:
        return None, "⏳ api timeout"
    except requests.exceptions.RequestException:
        return None, "⚠️ network error"
    except:
        return None, "⚠️ server error"

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(
        msg,
        sc(
            "🔥 vip manual like bot\n\n"
            "📌 available command :\n\n"
            "⚡ /like uid\n\n"
            "📝 example :\n"
            "/like 123456789\n\n"
            "ℹ️ note :\n"
            "• private + group supported\n"
            "• daily api limit apply"
        ) + footer()
    )

# ================= MANUAL LIKE =================
@bot.message_handler(commands=["like"])
def manual_like(msg):
    user_id = msg.from_user.id
    now = time.time()

    # ⏳ Cooldown check
    if user_id in user_last_used and now - user_last_used[user_id] < COOLDOWN:
        wait = int(COOLDOWN - (now - user_last_used[user_id]))
        bot.reply_to(msg, sc(f"⏳ wait {wait} sec before next request") + footer())
        return

    parts = msg.text.split()

    if len(parts) != 2:
        bot.reply_to(
            msg,
            sc("❌ correct format:\n/like 123456789") + footer()
        )
        return

    uid = parts[1]

    if not uid.isdigit():
        bot.reply_to(msg, sc("❌ uid must be numbers only") + footer())
        return

    user_last_used[user_id] = now

    m = bot.reply_to(
        msg,
        sc(f"🔥 manual like\n\n⚡ uid : {uid}\n⏳ sending likes...") + footer()
    )

    data, err = call_api(uid)

    if err:
        bot.edit_message_text(sc(f"❌ like failed\n\n{err}") + footer(), msg.chat.id, m.message_id)
        return

    likes_before = data.get("LikesbeforeCommand", 0)
    likes_after = data.get("LikesafterCommand", 0)
    likes = likes_after - likes_before

    # ❌ ZERO LIKE CONDITION
    if likes <= 0:
        bot.edit_message_text(
            sc(
                "❌ like failed\n\n"
                "is player ne max like kahi se le rakhe hai\n"
                "kal try kare"
            ) + footer(),
            msg.chat.id,
            m.message_id
        )
        return

    # ✅ SUCCESS
    bot.edit_message_text(
        sc(
            "✅ like successful\n\n"
            f"👤 playername : {data.get('PlayerNickname')}\n"
            f"🆔 uid : {uid}\n\n"
            f"👍 likes before : {likes_before}\n"
            f"🔥 likes after : {likes_after}\n"
            f"🎯 likes given : {likes}\n\n"
            f"📈 remaining : {data.get('remaining','-')}\n"
            f"🌍 region : IND\n"
            f"⚙️ status : success"
        ) + footer(),
        msg.chat.id,
        m.message_id
    )

# ================= UNKNOWN COMMAND =================
@bot.message_handler(func=lambda m: m.text.startswith("/"))
def unknown(msg):
    bot.reply_to(msg, sc("❌ unknown command\nuse /start") + footer())

# ================= RUN =================
print("manual like bot running...")
bot.infinity_polling()