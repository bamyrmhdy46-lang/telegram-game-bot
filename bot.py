import sqlite3

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


TOKEN = "8349182537:AAFZBNA2XHOWWqcDjY7vlPGyw6HG8UlQSlY"

ADMIN_ID = 8876602895


conn = sqlite3.connect("games.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    name TEXT,
    description TEXT,
    photo TEXT,
    link TEXT
)
""")

conn.commit()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🎮 لیست بازی‌ها"]
    ]

    await update.message.reply_text(
        "🎮 به ربات معرفی بازی خوش آمدید",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )



async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id == ADMIN_ID:

        await update.message.reply_text(
            "👑 پنل ادمین\n\n"
            "فرمت افزودن بازی:\n"
            "/add نام | توضیحات | عکس | لینک دانلود"
        )

    else:

        await update.message.reply_text(
            "⛔ دسترسی ندارید"
        )



async def add_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    data = update.message.text.replace("/add", "").strip()

    parts = [x.strip() for x in data.split("|")]

    if len(parts) != 4:
        await update.message.reply_text(
            "❌ فرمت اشتباه است\n\n"
            "نمونه:\n"
            "/add نام | توضیحات | عکس | لینک"
        )
        return

    name = parts[0]
    desc = parts[1]
    photo = parts[2]
    link = parts[3]

    cursor.execute(
        "INSERT INTO games VALUES (?,?,?,?)",
        (name, desc, photo, link)
    )

    conn.commit()

    await update.message.reply_text(
        "✅ بازی اضافه شد"
    )



async def list_games(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("SELECT name FROM games")

    result = cursor.fetchall()


    if not result:

        await update.message.reply_text(
            "هنوز بازی‌ای ثبت نشده"
        )

        return


    keyboard = []

    for game in result:

        keyboard.append(
            [game[0]]
        )


    await update.message.reply_text(
        "🎮 یک بازی انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )



async def show_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.message.text


    cursor.execute(
        "SELECT * FROM games WHERE name=?",
        (name,)
    )

    game = cursor.fetchone()


    if game:

        name, desc, photo, link = game


        button = [
            [
                InlineKeyboardButton(
                    "⬇️ دانلود",
                    url=link
                )
            ]
        ]


        await update.message.reply_photo(
            photo=photo,
            caption=f"🎮 {name}\n\n{desc}",
            reply_markup=InlineKeyboardMarkup(button)
        )



app = Application.builder().token(TOKEN).build()


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("add", add_game))


app.add_handler(
    MessageHandler(
        filters.Regex("🎮 لیست بازی‌ها"),
        list_games
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT,
        show_game
    )
)


print("ربات روشن شد 🎮")

app.run_polling()
