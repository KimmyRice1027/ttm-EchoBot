import logging
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Developer / Owner ID (မင်းရဲ့ ID)
DEVELOPER_ID = 6404389665
ADMIN_FILE = "admins.txt"

# Admin များကို ဖိုင်ထဲမှ ဖတ်ယူရန်
def load_admins():
    admins = {DEVELOPER_ID}  # Developer က အမြဲတမ်း Admin/Owner ဖြစ်သည်
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

# Developer သီးသန့် Admin အသစ် ထည့်ခွင့်ပြုသည့် Command (/addadmin [User ID])
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

# Admin များသာ ဝင်သုံးနိုင်သော Panel
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    admins = load_admins()

    if user_id not in admins:
        await update.message.reply_text("⛔ ဒီနေရာကို ဝင်ရောက်ခွင့် မရှိပါဘူး။")
        return

    await update.message.reply_text(
        "👑 **Admin Panel သို့ ကြိုဆိုပါတယ်**\n\n"
        "ဒီနေရာမှ အော်ဒါများနှင့် ငွေလွှဲပြေစာများကို စစ်ဆေးနိုင်ပါတယ်။"
    )

# Button တုံ့ပြန်မှုများ
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "mlbb":
        await query.edit_message_text(text="💎 MLBB Diamonds ဝယ်ယူရန် ကျေးဇူးပြု၍ User ID နဲ့ Server ID ကို ပေးပို့ပါ။")
    elif query.data == "pubg":
        await query.edit_message_text(text="🛒 PUBG UC ဝယ်ယူရန် ကျေးဇူးပြု၍ Player ID ကို ပေးပို့ပါ။")

def main() -> None:
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing!")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(button))

    # Python ဗားရှင်းအသစ်များအတွက် Event Loop အမှားမတတ်စေရန် ဤကဲ့သို့ Run ပါ
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        application.run_polling()
    else:
        asyncio.run(application.initialize())
        application.run_polling()

if __name__ == "__main__":
    main()
