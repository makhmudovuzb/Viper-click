"""
Viper Click WebApp Bot
/start
/help
/admin_support
/admin_panel

Aiogram 3.x
"""

import asyncio
import logging
import os
from html import escape

from aiohttp import web

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonCommands,
    Message,
    WebAppInfo
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


# =========================================================
# SOZLAMALAR
# =========================================================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "YANGI_TOKENINGNI_SHU_YERGA_QO'Y"
)

WEBAPP_URL = "https://viper-click-enhancednew.vercel.app/"
DEV_USERNAME = "Makhmudov_h001"

# ADMIN SUPPORT ID VA PAROL
ADMIN_SUPPORT_ID = 8605234251
ADMIN_PASSWORD = "MH2013MH"

# MAJBURIY OBUNA KANALLARI
CHANNELS = [
    {"id": -1004336927865, "link": "https://t.me/+dlgHr-FEdGlmNTAy", "name": "1-Kanal"},
    {"id": -1004375273530, "link": "https://t.me/+EiaU473srG5hM2Uy", "name": "2-Kanal"},
    {"id": -1003976183058, "link": "https://t.me/+8NEOsZ0LnRk5NjNi", "name": "3-Kanal"},
]


# =========================================================
# FOYDALANUVCHILAR BAZASI VA XOTIRA
# =========================================================

registered_users = set()
support_users = {}


# =========================================================
# ROUTER VA STATES
# =========================================================

router = Router()


class SupportState(StatesGroup):
    waiting_message = State()


class AdminState(StatesGroup):
    waiting_password = State()
    waiting_broadcast_message = State()


# =========================================================
# OBUNANI TEKSHIRISH FUNKSIYASI
# =========================================================

async def check_subscription(bot: Bot, user_id: int) -> bool:
    if user_id == ADMIN_SUPPORT_ID:
        return True

    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logging.error(f"Kanal tekshirish xatosi {channel['id']}: {e}")
            continue
    return True


def sub_keyboard(ref_param: str | None = None):
    buttons = []
    for idx, ch in enumerate(CHANNELS, 1):
        buttons.append([InlineKeyboardButton(text=f"📢 {idx}-kanalga obuna bo'lish", url=ch["link"])])
    
    cb_data = f"check_sub:{ref_param}" if ref_param else "check_sub:none"
    buttons.append([InlineKeyboardButton(text="🔄 Tekshirish ✅", callback_data=cb_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================================================
# TUGMALAR
# =========================================================

def start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Viper Click'ni ochish",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Yordam",
                    callback_data="help"
                )
            ]
        ]
    )


def help_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Viper Click'ni ochish",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="📩 Dasturchiga yozish",
                    url=f"https://t.me/{DEV_USERNAME}"
                )
            ]
        ]
    )


def admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistikani ko'rish", callback_data="admin_stats")],
            [InlineKeyboardButton(text="📢 Barcha o'yinchilarga xabar yuborish", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close")]
        ]
    )


# =========================================================
# START
# =========================================================

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext, bot: Bot):
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0

    is_subscribed = await check_subscription(bot, user_id)
    ref = command.args

    if not is_subscribed:
        await message.answer(
            "⚠️ <b>Botdan va Mini App'dan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>",
            reply_markup=sub_keyboard(ref)
        )
        return

    if message.from_user:
        registered_users.add(user_id)

    await message.answer(
        "⚡ <b>VIPER CLICK</b>\n\n"
        "Xush kelibsiz!\n"
        "Coin to'plang, bonuslarni oling va "
        "reytingda yuqoriga ko'tariling!",
        reply_markup=start_keyboard()
    )


# =========================================================
# OBUNANI TEKSHIRISH CALLBACK
# =========================================================

@router.callback_query(F.data.startswith("check_sub"))
async def cb_check_sub(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    is_subscribed = await check_subscription(bot, user_id)

    if is_subscribed:
        registered_users.add(user_id)
        await call.message.delete()
        await call.message.answer(
            "⚡ <b>VIPER CLICK</b>\n\n"
            "Xush kelibsiz!\n"
            "Coin to'plang, bonuslarni oling va "
            "reytingda yuqoriga ko'tariling!",
            reply_markup=start_keyboard()
        )
        await call.answer("✅ Rahmat! Barcha kanallarga obuna bo'ldingiz.", show_alert=True)
    else:
        await call.answer("❌ Hamma kanallarga obuna bo'lmadingiz! Iltimos, qayta tekshiring.", show_alert=True)


# =========================================================
# HELP
# =========================================================

@router.message(Command("help"))
async def cmd_help(message: Message, bot: Bot):
    if not await check_subscription(bot, message.from_user.id):
        await message.answer("⚠️ Botdan foydalanish uchun kanallarga obuna bo'ling!", reply_markup=sub_keyboard())
        return

    await message.answer(
        "🛠️ <b>Viper Click — Yordam</b>\n\n"
        "/start — Botni ochish\n"
        "/help — Yordam\n"
        "/admin_support — Admin bilan bog'lanish",
        reply_markup=help_keyboard()
    )


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Botni ishlatish uchun /start bosing "
        "va o'yinni oching."
    )


# =========================================================
# ADMIN PANEL
# =========================================================

@router.message(Command("admin_panel"))
async def cmd_admin_panel(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_SUPPORT_ID:
        await message.answer("❌ Siz admin emassiz!")
        return

    await message.answer("🔐 Admin panelga kirish uchun maxfiy parolni kiriting:")
    await state.set_state(AdminState.waiting_password)


@router.message(AdminState.waiting_password)
async def check_admin_password(message: Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await state.clear()
        await message.answer(
            "👑 <b>Admin Panelliga xush kelibsiz!</b>\n\nPastdagi tugmalarni bosing:",
            reply_markup=admin_keyboard()
        )
    else:
        await message.answer("❌ Parol noto'g'ri! Qaytadan urinib ko'ring yoki /start bosing.")


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    if call.from_user.id != ADMIN_SUPPORT_ID:
        await call.answer("Taqiqlangan!", show_alert=True)
        return

    count = len(registered_users)
    stats_text = (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"👥 <b>Jami o'yinchilar soni:</b> {count} ta\n"
        f"📩 <b>Support bog'lanishlar:</b> {len(support_users)} ta"
    )
    await call.message.answer(stats_text)
    await call.answer()


@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_SUPPORT_ID:
        await call.answer("Taqiqlangan!", show_alert=True)
        return

    await call.message.answer(
        "📢 <b>Barcha o'yinchilarga yubormoqchi bo'lgan xabaringizni yuboring:</b>\n\n"
        "<i>Matn, rasm yoki video yuborishingiz mumkin. Bekor qilish uchun /start bosing.</i>"
    )
    await state.set_state(AdminState.waiting_broadcast_message)
    await call.answer()


@router.message(AdminState.waiting_broadcast_message, ~F.text.startswith("/"))
async def send_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    await message.answer("🚀 Xabar barcha o'yinchilarga yuborilmoqda...")

    success = 0
    failed = 0

    for user_id in list(registered_users):
        try:
            await message.copy_to(chat_id=user_id)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await message.answer(
        "✅ <b>Xabar yuborish yakunlandi!</b>\n\n"
        f"🟢 <b>Muvaffaqiyatli:</b> {success} ta\n"
        f"🔴 <b>Yetib bormadi (bloklagan):</b> {failed} ta"
    )
    await state.clear()


@router.callback_query(F.data == "admin_close")
async def cb_admin_close(call: CallbackQuery):
    await call.message.delete()
    await call.answer()


# =========================================================
# ADMIN SUPPORT AMALLARI
# =========================================================

@router.message(Command("admin_support"))
async def admin_support(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription(bot, message.from_user.id):
        await message.answer("⚠️ Botdan foydalanish uchun kanallarga obuna bo'ling!", reply_markup=sub_keyboard())
        return

    support_text = (
        "🛠️ <b>Admin Support</b>\n\n"
        "Viper Click bo‘yicha muammo, xatolik yoki "
        "savolingiz bo‘lsa, shu yer orqali admin bilan "
        "bog‘lanishingiz mumkin.\n\n"
        "📩 Muammoingizni imkon qadar aniq yozing va "
        "kerak bo‘lsa, screenshot yuboring.\n\n"
        "⚡ Admin imkon qadar tezroq javob beradi.\n\n"
        "🙏 Tushunishingiz uchun rahmat!"
    )

    await message.answer(support_text)
    await state.set_state(SupportState.waiting_message)


@router.message(SupportState.waiting_message, ~F.text.startswith("/"))
async def receive_support_message(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    if not user:
        return

    name = user.first_name or "Foydalanuvchi"
    username = f"@{user.username}" if user.username else "@username_yoq"
    user_id = user.id

    admin_info = (
        f"👤 <b>{escape(name)} sizga xabar yubordi:</b>\n"
        f"<b>Username:</b> {username}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        f"👇 <i>Javob berish uchun ushbu xabarga Reply qiling:</i>"
    )

    try:
        info_message = await bot.send_message(
            chat_id=ADMIN_SUPPORT_ID,
            text=admin_info
        )

        copied_message = await message.copy_to(
            chat_id=ADMIN_SUPPORT_ID,
            reply_to_message_id=info_message.message_id
        )

        support_users[copied_message.message_id] = user_id
        await message.answer("Xabar jo'natildi✅️")

    except Exception as e:
        logging.error(f"Support xatosi: {e}")
        await message.answer(
            "❌ Xabar yuborishda xatolik yuz berdi. "
            "Iltimos, birozdan keyin qayta urinib ko‘ring."
        )


@router.message(F.from_user.id == ADMIN_SUPPORT_ID)
async def admin_reply(message: Message, bot: Bot):
    if not message.reply_to_message:
        return

    replied_message_id = message.reply_to_message.message_id
    user_id = support_users.get(replied_message_id)

    if not user_id:
        await message.reply("❌ Bu xabarga tegishli foydalanuvchi ID topilmadi (eski xabar bo'lishi mumkin).")
        return

    try:
        await message.copy_to(chat_id=user_id)
        await message.reply("✅ Javob foydalanuvchiga yuborildi.")
    except Exception as e:
        logging.error(f"Admin reply xatosi: {e}")
        await message.reply("❌ Foydalanuvchiga javob yuborilmadi (Foydalanuvchi botni bloklagan bo'lishi mumkin).")


# =========================================================
# RENDER UCHUN WEB SERVER (24/7 ISHLASHI UCHUN)
# =========================================================

async def start_web_server():
    app = web.Application()

    async def home(request):
        return web.Response(text="Viper Click WebApp Bot is running!")

    app.router.add_get("/", home)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


# =========================================================
# MAIN
# =========================================================

async def main():
    logging.basicConfig(level=logging.INFO)

    # Render portini ushlab turish uchun veb-serverni ishga tushiramiz
    await start_web_server()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.set_my_commands([
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
        BotCommand(command="admin_support", description="Admin bilan bog'lanish"),
        BotCommand(command="admin_panel", description="Admin Panel")
    ])

    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    print("🔥 Viper Click WebApp Bot ishga tushdi!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
