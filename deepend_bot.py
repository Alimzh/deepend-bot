import time
from collections import defaultdict

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

TOKEN = "YOUR_TOKEN"
OWNER_ID = 557486407

# ======================
# STATE
# ======================

state = {}
data = {}
spam_counter = defaultdict(int)

# هر session = یک “ارسال واقعی”
session_sent = defaultdict(bool)

SPAM_LIMIT = 7

# ======================
# MAIN UI (single message)
# ======================

MAIN_TEXT = """🎬 به Deepend Bot خوش اومدی

اینجا جاییه که داستان‌ها زنده می‌شن
فرقی نداره ترسناک باشه، جنایی یا حتی یه خاطره عاشقانه….

آماده‌ای داستانتو تعریف کنی؟"""

MAIN_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("📖 ارسال داستان", callback_data="story")],
    [InlineKeyboardButton("💬 پیشنهاد و انتقاد", callback_data="feedback")],
    [InlineKeyboardButton("👤 ارتباط با من", url="https://t.me/imAryo")],
    [InlineKeyboardButton("📺 یوتیوب Deepend", url="https://youtube.com/@adeepend")]
])

# ======================
# HELPERS
# ======================

def reset_user(uid):
    state.pop(uid, None)
    data.pop(uid, None)
    session_sent.pop(uid, None)

def can_send(uid):
    return spam_counter[uid] < SPAM_LIMIT

def add_send(uid):
    spam_counter[uid] += 1

# ======================
# SAFE EDIT
# ======================

async def safe_edit(query, text, kb):
    try:
        await query.message.edit_text(text, reply_markup=kb)
    except:
        try:
            await query.message.edit_caption(text, reply_markup=kb)
        except:
            await query.message.reply_text(text, reply_markup=kb)

# ======================
# START
# ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    reset_user(uid)

    await update.message.reply_photo(
        photo=open("botStart.jpg", "rb"),
        caption=MAIN_TEXT,
        reply_markup=MAIN_KB
    )

# ======================
# CALLBACK
# ======================

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    d = q.data

    # RESET TO START
    if d == "back" or d == "end":
        reset_user(uid)
        await safe_edit(q, MAIN_TEXT, MAIN_KB)
        return

    # ================= STORY =================

    if d == "story":
        state[uid] = "story_cat"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👻 ترسناک", callback_data="cat_h")],
            [InlineKeyboardButton("🔪 جنایی", callback_data="cat_c")],
            [InlineKeyboardButton("❤️ عاشقانه", callback_data="cat_l")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="end")]
        ])

        await safe_edit(q, "لطفا نوع داستانتو انتخاب کن", kb)

    elif d.startswith("cat_"):
        state[uid] = "story_anon"

        if d == "cat_h":
            data[uid] = {"cat": "ترسناک"}
        elif d == "cat_c":
            data[uid] = {"cat": "جنایی"}
        else:
            data[uid] = {"cat": "عاشقانه"}

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ بله", callback_data="sa"),
             InlineKeyboardButton("❌ خیر", callback_data="sn")],
            [InlineKeyboardButton("🔁 تغییر نوع داستان", callback_data="story")]
        ])

        await safe_edit(q, "میخوای داستانتو ناشناس بفرستی؟", kb)

    elif d in ["sa", "sn"]:
        state[uid] = "writing_story"
        data[uid]["anon"] = (d == "sa")

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ انصراف", callback_data="end")]
        ])

        await safe_edit(
            q,
            "لطفا داستانتو بنویس یا ویس/عکس/ویدیو ارسال کن",
            kb
        )

    # ================= FEEDBACK =================

    elif d == "feedback":
        state[uid] = "feedback_anon"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ بله", callback_data="fa"),
             InlineKeyboardButton("❌ خیر", callback_data="fn")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="end")]
        ])

        await safe_edit(q, "میخوای ناشناس ارسال کنی؟", kb)

    elif d in ["fa", "fn"]:
        state[uid] = "writing_feedback"
        data[uid] = {"anon": (d == "fa")}

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ انصراف", callback_data="end")]
        ])

        await safe_edit(q, "پیشنهاد یا انتقادتو بفرست", kb)

# ======================
# MESSAGE HANDLER
# ======================

async def content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg = update.message

    if uid not in state:
        return

    if not can_send(uid):
        await msg.reply_text("⛔ محدودیت ارسال")
        return

    step = state[uid]
    add_send(uid)

    # ================= STORY =================

    if step == "writing_story":

        cat = data[uid]["cat"]
        anon = data[uid].get("anon", True)

        if anon:
            sender = "ناشناس"
        else:
            sender = f"@{update.effective_user.username}" if update.effective_user.username else "بدون نام کاربری"

        header = f"📖 داستان\n👤 {sender}\n📂 {cat}\n---"

        await send_to_owner(update, context, header)

        session_sent[uid] = True

        await msg.reply_text(
            "اگر هنوز مونده لطفا ادامه بده",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏁 پایان", callback_data="end")]
            ])
        )

    # ================= FEEDBACK =================

    elif step == "writing_feedback":

        anon = data[uid].get("anon", True)

        if anon:
            sender = "ناشناس"
        else:
            sender = f"@{update.effective_user.username}" if update.effective_user.username else "بدون نام کاربری"

        header = f"💬 پیشنهاد\n👤 {sender}\n---"

        await send_to_owner(update, context, header)

        session_sent[uid] = True

        await msg.reply_text(
            "اگر هنوز مونده لطفا ادامه بده",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏁 پایان", callback_data="end")]
            ])
        )

# ======================
# SEND OWNER
# ======================

async def send_to_owner(update, context, header):
    msg = update.message

    if msg.text:
        await context.bot.send_message(OWNER_ID, header + "\n" + msg.text)

    elif msg.photo:
        await context.bot.send_photo(OWNER_ID, msg.photo[-1].file_id, caption=header)

    elif msg.video:
        await context.bot.send_video(OWNER_ID, msg.video.file_id, caption=header)

    elif msg.voice:
        await context.bot.send_voice(OWNER_ID, msg.voice.file_id, caption=header)

# ======================
# APP
# ======================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(cb))
app.add_handler(MessageHandler(filters.ALL, content))

print("Bot running...")
app.run_polling()
