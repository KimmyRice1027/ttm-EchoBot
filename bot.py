import logging
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Developer / Owner ID
DEVELOPER_ID = 6404389665
ADMIN_FILE = "admins.txt"

# Conversation States (ဝယ်ယူသည့်အဆင့်များ)
ENTER_INFO, SELECT_PKG, UPLOAD_PAYMENT = range(3)

# Admin များကို ဖိုင်ထဲမှ ဖတ်ယူရန်
def load_admins():
    admins = {DEVELOPER_ID}
    if os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, "r") as f:
            for line in f:
                try:
                    admins.add(int(line.strip()))
                except ValueError:
                    pass
    return admins

# Admin အသစ်ကို ဖိုင်ထဲသို့ သိမ်းရန်
def save_admin(admin_id):
    admins = load_admins()
    if admin_id not in admins:
        with open(ADMIN_FILE, "a") as f:
            f.write(f"{admin_id}\n")

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("💎 MLBB Diamonds", callback_data="mlbb"),
            InlineKeyboardButton("🛒 PUBG UC", callback_data="pubg"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"မင်္ဂလာပါ {user.first_name}!\n\n"
        "MLBB Diamonds နဲ့ PUBG UC များကို စိတ်ချယုံကြည်စွာ ဝယ်ယူနိုင်ပါတယ်။\n"
        "ဝယ်ယူလိုသော ဂိမ်းကို ရွေးချယ်ပါ -",
        reply_markup=reply_markup,
    )
    return ConversationHandler.END

# ဂိမ်းရွေးချယ်ပြီးပါက ID တောင်းခံခြင်း
async def game_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    game = query.data
    context.user_data['game'] = "MLBB Diamonds" if game == "mlbb" else "PUBG UC"
    
    if game == "mlbb":
        text = "💎 **MLBB Diamonds ဝယ်ယူခြင်း**\n\nကျေးဇူးပြု၍ သင့်ရဲ့ **User ID နဲ့ Server ID** ကို ပို့ပေးပါ။\n(ဥပမာ - `12345678 (1234)`)"
    else:
        text = "🛒 **PUBG UC ဝယ်ယူခြင်း**\n\nကျေးဇူးပြု၍ သင့်ရဲ့ **Player ID** ကို ပို့ပေးပါ။\n(ဥပမာ - `5123456789`)"
        
    await query.edit_message_text(text=text, parse_mode="Markdown")
    return ENTER_INFO

# User ID / Player ID လက်ခံရယူခြင်း (ခလုတ်များ သေချာပေါက် ပေါ်လာစေရန် ပြင်ဆင်ပြီး)
async def receive_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_info = update.message.text
    context.user_data['user_info'] = user_info
    
    game = context.user_data.get('game', 'MLBB Diamonds')
    
    if "MLBB" in game:
        keyboard = [
            [InlineKeyboardButton("86 Diamonds - 5,000 MMK", callback_data="pkg_ml_86")],
            [InlineKeyboardButton("172 Diamonds - 10,000 MMK", callback_data="pkg_ml_172")],
            [InlineKeyboardButton("Weekly Diamond Pass - 6,000 MMK", callback_data="pkg_ml_wdp")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("60 UC - 3,500 MMK", callback_data="pkg_pubg_60")],
            [InlineKeyboardButton("325 UC - 17,500 MMK", callback_data="pkg_pubg_325")]
        ]
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ အချက်အလက် လက်ခံရရှိပါပြီ။\nအကောင့်အချက်အလက်: `{user_info}`\n\nအောက်ပါ Package များထဲမှ လိုချင်သည်ကို ရွေးချယ်ပါ -",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SELECT_PKG

# Package ရွေးချယ်ခြင်း
async def select_package(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    pkg_data = query.data
    pkg_names = {
        "pkg_ml_86": "86 Diamonds (5,000 MMK)",
        "pkg_ml_172": "172 Diamonds (10,000 MMK)",
        "pkg_ml_wdp": "Weekly Diamond Pass (6,000 MMK)",
        "pkg_pubg_60": "60 UC (3,500 MMK)",
        "pkg_pubg_325": "325 UC (17,500 MMK)"
    }
    
    selected_pkg = pkg_names.get(pkg_data, "Custom Package")
    context.user_data['package'] = selected_pkg
    
    payment_text = (
        f"🛒 **ရွေးချယ်ထားသော ပက်ကေ့ဂျ်:** {selected_pkg}\n\n"
        "ငွေပေးချေရန် ငွေလွှဲနိုင်သော Account များ -\n"
        "• **KBZPay:** `09123456789` (Mg Mg)\n"
        "• **Wave Money:** `09987654321` (Mg Mg)\n\n"
        "ငွေလွှဲပြီးပါက **ငွေလွှဲပြေစာ (Screenshot ပုံ)** ကို ဤ Bot ထဲသို့ တိုက်ရိုက် ပို့ပေးပါ။"
    )
    await query.edit_message_text(text=payment_text, parse_mode="Markdown")
    return UPLOAD_PAYMENT

# ငွေလွှဲပြေစာလက်ခံပြီး Admin ထံ ပို့ပေးခြင်း
async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1]
    user = update.effective_user
    
    game = context.user_data.get('game', 'Unknown Game')
    user_info = context.user_data.get('user_info', 'N/A')
    package = context.user_data.get('package', 'N/A')
    
    await update.message.reply_text(
        "✅ သင့်ရဲ့ ငွေလွှဲပြေစာနှင့် အော်ဒါကို အောင်မြင်စွာ လက်ခံရရှိပါပြီ။\n"
        "Admin မှ စစ်ဆေးပြီး အမြန်ဆုံး ဖြည့်သွင်းပေးပါမည်။ ကျေးဇူးတင်ပါတယ်။ 🙏"
    )
    
    admins = load_admins()
    admin_msg = (
        f"🔔 **အော်ဒါအသစ် ရောက်ရှိပါပြီ!**\n\n"
        f"👤 ဝယ်ယူသူ: {user.full_name} (@{user.username or 'No Username'})\n"
        f"🆔 User ID: `{user.id}`\n"
        f"🎮 ဂိမ်း: {game}\n"
        f"📝 အကောင့်အချက်အလက်: `{user_info}`\n"
        f"📦 ပက်ကေ့ဂျ်: {package}"
    )
    
    application = context.application
    for admin_id in admins:
        try:
            await application.bot.send_photo(
                chat_id=admin_id,
                photo=photo.file_id,
                caption=admin_msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send order notification to admin {admin_id}: {e}")
            
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ ဝယ်ယူမှုကို ဖျက်သိမ်းလိုက်ပါပြီ။ ပြန်စရန် /start ကိုနှိပ်ပါ။")
    return ConversationHandler.END

# Developer သီးသန့် Admin အသစ် ထည့်ခွင့်ပြုသည့် Command
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id != DEVELOPER_ID:
        await update.message.reply_text("⛔ ဒီ Command ကို Developer သာ အသုံးပြုခွင့်ရှိပါတယ်။")
        return

    if not context.args:
        await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ ထည့်လိုသော User ID ကို တွဲလျက်ရေးပါ။\nဥပမာ - `/addadmin 123456789`")
        return

    try:
        new_admin_id = int(context.args[0])
        save_admin(new_admin_id)
        await update.message.reply_text(f"✅ အောင်မြင်ပါသည်! User ID `{new_admin_id}` ကို Admin အဖြစ် သတ်မှတ်လိုက်ပါပြီ။")
    except ValueError:
        await update.message.reply_text("❌ မှားယွင်းနေပါသည်၊ User ID သည် ဂဏန်းဖြစ်ရပါမည်။")

# Admin များသာ ဝင်သုံးနိုင်သော Panel (/admin)
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    admins = load_admins()

    if user_id not in admins:
        await update.message.reply_text("⛔ ဒီနေရာကို ဝင်ရောက်ခွင့် မရှိပါဘူး။")
        return

    keyboard = [
        [InlineKeyboardButton("📦 Pending Orders Info", callback_data="admin_orders")],
        [InlineKeyboardButton("👥 Admin List", callback_data="admin_list")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👑 **Owner / Admin Control Panel**\n\nအောက်ပါ မီနူးများမှ တစ်ခုကို ရွေးချယ်ပါ -",
        reply_markup=reply_markup
    )

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "admin_orders":
        await query.edit_message_text(text="📦 အော်ဒါအသစ်များကို ဖောက်သည်များ ငွေလွှဲပြေစာ ပို့လိုက်သည်နှင့် ဤ Bot မှတစ်ဆင့် Admin ဆီသို့ တိုက်ရိုက် ပို့ပေးပါမည်။")
    elif query.data == "admin_list":
        admins = load_admins()
        admin_text = "👥 **Active Admins List:**\n" + "\n".join([f"- `{aid}`" for aid in admins])
        await query.edit_message_text(text=admin_text, parse_mode="Markdown")

async def run_bot():
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing!")

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(game_choice, pattern="^(mlbb|pubg)$")
        ],
        states={
            ENTER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_info)],
            SELECT_PKG: [CallbackQueryHandler(select_package, pattern="^pkg_")],
            UPLOAD_PAYMENT: [MessageHandler(filters.PHOTO, receive_payment)]
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
        per_message=True
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_buttons, pattern="^admin_"))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    stop_event = asyncio.Event()
    await stop_event.wait()

def main() -> None:
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
