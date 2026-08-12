import telebot
from telebot import types
import json
import os

TOKEN = os.getenv ( "8851055301:AAGgIZq7YU7uHiIFTZL5sK2P93vV60jmEqg")

CHANNELS = [
    "@sbrxls",
    "@sbrxlss"
]

ADMIN_ID = 7771705739

bot = telebot.TeleBot(TOKEN)

DB_FILE = "kinolar.json"

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        kinolar = json.load(f)
else:
    kinolar = {}


def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(kinolar, f, ensure_ascii=False, indent=2)


def subscribed(user_id):
    for channel in CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)

            if member.status not in ["member", "administrator", "creator"]:
                return False

        except Exception:
            return False

    return True


@bot.message_handler(commands=["start"])
def start(message):

    if not subscribed(message.from_user.id):

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "📢 1-kanal",
                url="https://t.me/sbrxls"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "📢 2-kanal",
                url="https://t.me/sbrxlss"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "✅ Tekshirish",
                callback_data="check"
            )
        )

        bot.send_message(
            message.chat.id,
            "🔐 Botdan foydalanish uchun ikkala kanalga ham obuna bo‘ling!",
            reply_markup=markup
        )

        return

    bot.send_message(
        message.chat.id,
        "🎬 Kino kodini yuboring.\n\nMasalan: 1234"
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "check"
)
def check(call):

    if subscribed(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.send_message(
            call.message.chat.id,
            "🎬 Kino kodini yuboring."
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Ikkala kanalga ham obuna bo‘ling!",
            show_alert=True
        )


@bot.message_handler(commands=["admin"])
def admin(message):

    if message.from_user.id != ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "❌ Siz admin emassiz."
        )
        return

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.add("➕ Kino qo‘shish")
    markup.add("📋 Kinolar")

    bot.send_message(
        message.chat.id,
        "👑 ADMIN PANEL",
        reply_markup=markup
    )


@bot.message_handler(
    func=lambda message: message.text == "➕ Kino qo‘shish"
)
def add_movie(message):

    if message.from_user.id != ADMIN_ID:
        return

    msg = bot.send_message(
        message.chat.id,
        "🔢 Kino kodini yuboring:"
    )

    bot.register_next_step_handler(msg, get_code)


def get_code(message):

    if message.from_user.id != ADMIN_ID:
        return

    code = message.text.strip()

    if code in kinolar:
        bot.send_message(
            message.chat.id,
            "❌ Bu kod allaqachon mavjud."
        )
        return

    msg = bot.send_message(
        message.chat.id,
        "📝 Kino nomini yuboring:"
    )

    bot.register_next_step_handler(
        msg,
        get_name,
        code
    )


def get_name(message, code):

    if message.from_user.id != ADMIN_ID:
        return

    name = message.text.strip()

    msg = bot.send_message(
        message.chat.id,
        "🎥 Endi kino videosini yuboring:"
    )

    bot.register_next_step_handler(
        msg,
        get_video,
        code,
        name
    )


def get_video(message, code, name):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.video:

        msg = bot.send_message(
            message.chat.id,
            "❌ Bu video emas. Videoni yuboring:"
        )

        bot.register_next_step_handler(
            msg,
            get_video,
            code,
            name
        )

        return

    kinolar[code] = {
        "name": name,
        "file_id": message.video.file_id
    }

    save_db()

    bot.send_message(
        message.chat.id,
        f"✅ Kino qo‘shildi!\n\n"
        f"🔢 Kod: {code}\n"
        f"🎬 Nomi: {name}"
    )


@bot.message_handler(
    func=lambda message: message.text == "📋 Kinolar"
)
def movie_list(message):

    if message.from_user.id != ADMIN_ID:
        return

    if not kinolar:
        bot.send_message(
            message.chat.id,
            "📭 Hozircha kino yo‘q."
        )
        return

    text = "📋 KINOLAR:\n\n"

    for code, movie in kinolar.items():
        text += f"🔢 {code} — {movie['name']}\n"

    bot.send_message(
        message.chat.id,
        text
    )


@bot.message_handler(
    func=lambda message: True
)
def search_movie(message):

    if not subscribed(message.from_user.id):
        start(message)
        return

    code = message.text.strip()

    if code not in kinolar:

        bot.send_message(
            message.chat.id,
            "❌ Bunday kodli kino topilmadi."
        )

        return

    movie = kinolar[code]

    bot.send_video(
        message.chat.id,
        movie["file_id"],
        caption=f"🎬 {movie['name']}"
    )


print("🤖 Kino bot ishga tushdi!")

bot.infinity_polling()
