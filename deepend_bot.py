import time
from collections import defaultdict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
OWNER_USERNAME = "imAryo"

MAIN = InlineKeyboardMarkup([
    [InlineKeyboardButton("📖 ارسال داستان", callback_data="story")],
    [InlineKeyboardButton("💬 پیشنهاد و انتقاد", callback_data="feedback")],
    [InlineKeyboardButton("👤 ارتباط با من", url=f"https://t.me/{OWNER_USERNAME}")],
    [InlineKeyboardButton("📺 کانال یوتیوب Deepend", url="https://youtube.com/@adeepend")]
])
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8900626345:AAF59d1piwpWgy-i7wFAoH_2kAV4L6CoElY"
OWNER_USERNAME = "imAryo"
OWNER_ID = 557486407

# ======================
# STATE
# ======================

state = {}
data = {}
spam = defaultdict(list)

SPAM_LIMIT = 5
SPAM_WINDOW = 3600

# ======================
# HELPERS
# ======================

def hard_reset(uid):
    state.pop(uid, None)
    data.pop(uid, None)

def is_spam(uid):
    now = time.time()
    spam[uid] = [t for t in spam[uid] if now - t < SPAM_WINDOW]
    return len(spam[uid]) >= SPAM_LIMIT

def add_spam(uid):
    spam[uid].append(time.time())

# ======================
# START
# ======================
async def go_start(update, context):
    kb = MAIN
    text = "🎬 به Deepend Bot خوش اومدی"

    if update.callback_query:
        msg = update.callback_query.message

        try:
            await msg.edit_caption(text, reply_markup=kb)
        except:
            await msg.edit_text(text, reply_markup=kb)

    else:
        await update.message.reply_text(text, reply_markup=kb)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    hard_reset(uid)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 ارسال داستان و خاطرات", callback_data="story")],
        [InlineKeyboardButton("💬 پیشنهاد و انتقاد", callback_data="feedback")],
        [InlineKeyboardButton("👤 ارتباط با من", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("📺 کانال یوتیوب Deepend", url="https://youtube.com/@adeepend")]
    ])

    if update.message:
        await update.message.reply_photo(
            photo=open("botStart.jpg", "rb"),
            caption=
            "🎬 به Deepend Bot خوش اومدی\n\n"
            "اینجا جاییه که داستان‌ها زنده می‌شن…\n\n"
            "فرقی نداره ترسناک باشه، جنایی یا حتی یه خاطره عاشقانه….\n\n"
            "آماده‌ای داستانتو تعریف کنی؟",
            reply_markup=MAIN
        )
    else:
        await update.callback_query.message.reply_photo(
            photo=open("botStart.jpg", "rb"),
            caption=
            "🎬 به Deepend Bot خوش اومدی\n\n"
            "اینجا جاییه که داستان‌ها زنده می‌شن…\n\n"
            "فرقی نداره ترسناک باشه، جنایی یا حتی یه خاطره عاشقانه….\n\n"
            "آماده‌ای داستانتو تعریف کنی؟",
            reply_markup=MAIN
        )


# ======================
# CALLBACK
# ======================

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    d = q.data

    # STORY START
    if d == "story":
        state[uid] = "story_cat"

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👻 ترسناک", callback_data="cat_h"),
            ],
            [

                InlineKeyboardButton("🔪 جنایی", callback_data="cat_c"),
            ],
            [
                InlineKeyboardButton("❤️ عاشقانه", callback_data="cat_l"),
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back"),
            ]
        ])

        await q.message.edit_caption("نوع داستان رو انتخاب کن 👇", reply_markup=kb)

    # CATEGORY SELECTED
    elif d.startswith("cat_"):
        state[uid] = "ask_story_anon"
        data.setdefault(uid, {})

        if d == "cat_h":
            data[uid]["cat"] = "ترسناک"
        elif d == "cat_c":
            data[uid]["cat"] = "جنایی"
        elif d == "cat_l":
            data[uid]["cat"] = "عاشقانه"

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ناشناش", callback_data="sa"),
                InlineKeyboardButton("🙋 با نام کاربری", callback_data="sn"),
            ],
            [
                InlineKeyboardButton("❌ انصراف", callback_data="cancel_story")
            ]
        ])

        await q.message.edit_caption(
            "میخوای ناشناس ارسال بشه؟",
            reply_markup=kb
        )
    elif d in ["sa", "sn"]:
        data.setdefault(uid, {})
        data[uid]["anon"] = (d == "sa")

        state[uid] = "writing_story"

        await q.message.edit_caption(
            "حالا داستانتو بفرست ✨"
        )
        if d == "cat_h":
            data[uid]["cat"] = "ترسناک"
        elif d == "cat_c":
            data[uid]["cat"] = "جنایی"
        elif d == "cat_l":
            data[uid]["cat"] = "عاشقانه"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ انصراف", callback_data="cancel_story")]
        ])

        await q.message.edit_caption(
            "حالا داستانتو بفرست ✨\nمی‌تونی متن / عکس / صدا / ویدیو بفرستی",
            reply_markup=kb
        )

    # FEEDBACK START
    elif d == "feedback":
        state[uid] = "ask_feedback_anon"

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ ناشناس", callback_data="fa"),
                InlineKeyboardButton("🙋 با نام کاربری", callback_data="fn"),
            ],
            [
                InlineKeyboardButton("🔙 بازگشت", callback_data="back"),
            ]
        ])

        await q.message.edit_caption(
            "میخوای ناشناس ارسال بشه؟",
            reply_markup=kb
        )
    elif d in ["fa", "fn"]:
        data.setdefault(uid, {})
        data[uid]["anon"] = (d == "fa")

        state[uid] = "writing_feedback"

        await q.message.edit_caption(
            "حالا پیشنهاد یا انتقادتو بفرست ✨"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ انصراف", callback_data="cancel_feedback")]
        ])

        await q.message.edit_caption(
            "از اینکه به بهتر شدن ما کمک میکنی ممنونم\nلطفا پیامت رو بفرست",
            reply_markup=kb
        )

    elif d == "back":
        state.pop(uid, None)
        data.pop(uid, None)

        await q.message.edit_caption(
            "آماده‌ای داستانتو تعریف کنی؟",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 ارسال داستان", callback_data="story")],
                [InlineKeyboardButton("💬 پیشنهاد و انتقاد", callback_data="feedback")],
                [InlineKeyboardButton("👤 ارتباط با من", url=f"https://t.me/{OWNER_USERNAME}")],
                [InlineKeyboardButton("📺 کانال یوتیوب Deepend", url="https://youtube.com/@adeepend")]
            ])
        )

    # CANCEL STORY
    elif d == "cancel_story":
        hard_reset(uid)
        await go_start(update, context)

    # CANCEL FEEDBACK
    elif d == "cancel_feedback":
        hard_reset(uid)
        await go_start(update, context)

    # END
    elif d == "end":
        hard_reset(uid)

        msg = update.callback_query.message
        text = "🏠 برگشت به منو اصلی"

        try:
            await msg.edit_text(text, reply_markup=MAIN)
        except:
            await msg.edit_caption(text, reply_markup=MAIN)

# ======================
# CONTENT
# ======================

async def content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = update.message
    text = msg.text or ""

    state_now = state.get(uid)

    if not state_now:
        return

    # SPAM
    if is_spam(uid):
        await msg.reply_text("⏳ زیاد ارسال کردی")
        return

    add_spam(uid)

    cat = data.get(uid, {}).get("cat", "نامشخص")
    anon = data.get(uid, {}).get("anon", True)

    if anon:
        sender = "ناشناس"
    else:
        sender = f"@{update.effective_user.username}" if update.effective_user.username else "بدون یوزرنیم"

    # ======================
    # STORY
    # ======================
    if state_now == "writing_story":

        caption = f"📖 داستان\n📂 {data[uid]['cat']}\n👤 {sender}"

        try:
            if msg.text:
                await context.bot.send_message(OWNER_ID, caption + "\n\n" + msg.text)

            elif msg.voice:
                await context.bot.send_voice(OWNER_ID, msg.voice.file_id, caption=caption)

            elif msg.photo:
                await context.bot.send_photo(OWNER_ID, msg.photo[-1].file_id, caption=caption)

            elif msg.video:
                await context.bot.send_video(OWNER_ID, msg.video.file_id, caption=caption)

            elif msg.document:
                await context.bot.send_document(OWNER_ID, msg.document.file_id, caption=caption)

            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏁 پایان", callback_data="end")]
            ])

            await msg.reply_text("اگر میخوای ادامه بده و یا پایان رو بزن 👇", reply_markup=kb)

        except Exception as e:
            print(e)

    # ======================
    # FEEDBACK
    # ======================
    elif state_now == "writing_feedback":

        anon = data.get(uid, {}).get("anon", True)

        if anon:
            sender = "ناشناس"
        else:
            sender = f"@{update.effective_user.username}" if update.effective_user.username else "بدون یوزرنیم"

        caption = f"💬 پیشنهاد/انتقاد\n👤 {sender}"

        try:
            if msg.text:
                await context.bot.send_message(OWNER_ID, caption + "\n\n" + msg.text)

            elif msg.voice:
                await context.bot.send_voice(OWNER_ID, msg.voice.file_id, caption=caption)

            elif msg.photo:
                await context.bot.send_photo(OWNER_ID, msg.photo[-1].file_id, caption=caption)

            elif msg.video:
                await context.bot.send_video(OWNER_ID, msg.video.file_id, caption=caption)

            elif msg.document:
                await context.bot.send_document(OWNER_ID, msg.document.file_id, caption=caption)

            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ انصراف", callback_data="cancel_feedback")],
                [InlineKeyboardButton("🏁 پایان", callback_data="end")]
            ])

            await msg.reply_text("اگر تموم شد رو پایان بزن 👇", reply_markup=kb)

        except Exception as e:
            print(e)

# ======================
# APP
# ======================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(cb))
app.add_handler(MessageHandler(filters.ALL, content))

print("Deepend bot running...")
app.run_polling()
