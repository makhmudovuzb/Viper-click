"""
Viper Click Bot
/start
/help
/admin_support
/admin_panel

Aiogram 3.x

O'rnatish:
    pip install -U aiogram aiohttp

Ishga tushirish:
    python main.py
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
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


# =========================================================
# SOZLAMALAR
# =========================================================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "8902470609:AAGbpTMFkQJwvulkSll3HCLjkOIckkoATa8"
)

MINIAPP_LINK = "https://t.me/ViperClickBot?startapp=ref_w2ng4fr9s2"
MINIAPP_BASE = "https://t.me/ViperClickBot?startapp="
DEV_USERNAME = "Makhmudov_h001"

# ADMIN SUPPORT ID VA PAROL
ADMIN_SUPPORT_ID = 8605234251
ADMIN_PASSWORD = "MH2013MH"


# =========================================================
# FOYDALANUVCHILAR MA'LUMOTLAR BAZASI (Xotirada saqlash)
# =========================================================

# Botga kirgan barcha foydalanuvchilar ID to'plami
registered_users = set()


# =========================================================
# ROUTER
# =========================================================

router = Router()


# =========================================================
# STATES (HOLATLAR)
# =========================================================

class SupportState(StatesGroup):
    waiting_message = State()


class AdminState(StatesGroup):
    waiting_password = State()


# =========================================================
# SUPPORT USERLARINI SAQLASH
# =========================================================

# Admin ko'rgan xabar ID -> user ID
support_users = {}


# =========================================================
# START MATNI
# =========================================================

def start_text(name: str, referred: bool = False) -> str:
    name = escape(name)

    ref_line = (
        "\n🤝 Siz do'stingizning havolasi orqali keldingiz. "
        "Ro'yxatdan o'tganingizdan so'ng u bonus oladi!\n"
        if referred
        else ""
    )

    return (
        f"🐍 <b>Viper Click</b> ga xush kelibsiz, <b>{name}</b>!\n"
        f"{ref_line}\n"

        "Bu yerda har bir bosish sizga token olib keladi. "
        "Token yig'ing, o'yinlarda omadingizni sinang va "
        "<b>Viper Legend</b> darajasigacha ko'tarilib, "
        "reytingda yuqoriga chiqing! 🏆\n\n"

        "<b>Sizni nimalar kutmoqda:</b>\n"

        "⚡ <b>Tap-to-earn</b> — bosing, token ishlang. "
        "Zaryad o'zi tiklanadi\n"

        "📈 <b>Trading</b> — narx o'sadimi yoki tushadimi? "
        "To'g'ri topsangiz ×1.9\n"

        "🏢 <b>Biznes</b> — 10 ta biznesga investitsiya qiling\n"

        "🎲 <b>Qora quti</b> va 🗃 <b>Qutilar markazi</b> — "
        "tumorlar va sovrinlar\n"

        "🏦 <b>Bank</b> — kredit va depozit bilan balansni oshiring\n"

        "🎁 <b>Kunlik bonus</b> — har kuni kiring, "
        "7 kunlik seriya oxirida katta sovg'a\n"

        "💌 <b>Sovg'a</b> — do'stingizga kod orqali token yuboring\n"

        "👥 <b>Do'stlar</b> — har bir taklif qilingan do'st uchun "
        "+200 token\n\n"

        "🎟 Promo kodingiz bormi? Uni <b>Bosh</b> sahifada kiriting.\n\n"

        "Boshlash uchun pastdagi tugmani bosing 👇"
    )


# =========================================================
# HELP MATNI
# =========================================================

HELP_TEXT = (
    "❓ <b>Viper Click — yordam</b>\n\n"

    "<b>📱 Pastki menyu</b>\n"

    "🏠 <b>Bosh</b> — bosib token ishlash, kunlik bonus, "
    "promo kod, tumorlar\n"

    "🎲 <b>O'yin</b> — Ko'paytirish, Trading, Biznes, "
    "Qora quti, Qutilar markazi, Bank\n"

    "💌 <b>Sovg'a</b> — do'stga token yuborish va kelgan "
    "kodni kiritish\n"

    "🏆 <b>Reyting</b> — eng kuchli o'yinchilar ro'yxati\n"

    "👥 <b>Do'stlar</b> — shaxsiy havola va taklif "
    "qilinganlar soni\n\n"

    "<b>⚡ Token qanday ishlanadi?</b>\n"

    "Ekranga bosing — har bosishda token olasiz. "
    "Har bosish zaryad sarflaydi, zaryad esa har soniyada "
    "tiklanadi. Tumorlar va boostlar daromadni oshiradi.\n\n"

    "<b>🎮 O'yinlar</b>\n"

    "• O'yinlar balans <b>1000 token</b> ga yetganda ochiladi\n"

    "• <b>Trading</b> — har 12 soniyada yangi raund, "
    "yo'nalishni to'g'ri topsangiz ×1.9\n"

    "• <b>Biznes</b> — raund har 20 soniyada, natija barcha "
    "o'yinchilar uchun bir xil\n"

    "• <b>Qora quti</b> — 3 ta quti, kam tiksangiz yutish osonroq\n"

    "• <b>Bank</b> — kredit muddatida qaytarilmasa, "
    "balansdan ushlanadi. Depozitda ko'p tiksangiz foiz "
    "pastroq, muddat uzunroq\n\n"

    "<b>🎁 Bonuslar</b>\n"

    "• <b>Kunlik bonus</b> — 7 kun ketma-ket kiring, "
    "7-kuni eng katta sovg'a\n"

    "• <b>Promo kod</b> — Bosh sahifada kiriting, "
    "bir marta ishlaydi\n"

    "• <b>Do'st taklif qilish</b> — har bir do'st uchun "
    "+200 token\n\n"

    "<b>🏅 Unvonlar</b>\n"

    "Balansingiz oshgani sari unvon ham o'sadi: "
    "🐣 Yangi o'yinchi → 🥉 Bronza → 🥈 Kumush → "
    "🥇 Oltin → 💠 Platina → 💎 Olmos → 👑 Usta → "
    "🔥 Afsona → 🐍 Viper Legend → 🌟 O'lmas Viper\n\n"

    "<b>⚠️ Qoidalar</b>\n"

    "Avtoklikker yoki bot ishlatish taqiqlanadi. "
    "Aniqlansa, token jarima va <b>1 soatlik ban</b> beriladi. "
    "Halol o'ynang!\n\n"

    f"<b>📩 Aloqa:</b> muammo, savol yoki taklif bo'lsa "
    f"@{DEV_USERNAME} ga yozing."
)


# =========================================================
# TUGMALAR
# =========================================================

def start_keyboard(param: str | None = None):
    link = f"{MINIAPP_BASE}{param}" if param else MINIAPP_LINK
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 O'ynash", url=link)],
            [InlineKeyboardButton(text="❓ Yordam", callback_data="help")]
        ]
    )


def help_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 O'ynash", url=MINIAPP_LINK)],
            [InlineKeyboardButton(text="📩 Dasturchiga yozish", url=f"https://t.me/{DEV_USERNAME}")]
        ]
    )


def admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 O'yinchilar soni", callback_data="admin_players_count")],
            [InlineKeyboardButton(text="❌ Yopish", callback_data="admin_close")]
        ]
    )


# =========================================================
# START
# =========================================================

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()

    if message.from_user:
        registered_users.add(message.from_user.id)

    ref = command.args
    name = message.from_user.first_name if message.from_user else "do'st"

    await message.answer(
        start_text(name, referred=bool(ref)),
        reply_markup=start_keyboard(ref)
    )


# =========================================================
# HELP
# =========================================================

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=help_keyboard())


@router.callback_query(F.data == "help")
async def cb_help(call: CallbackQuery):
    await call.message.answer(HELP_TEXT, reply_markup=help_keyboard())
    await call.answer()


# =========================================================
# ADMIN PANEL (BUYRUG' VA PAROL TEKSHIRUV)
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
            "👑 <b>Admin Panelliga xush kelibsiz!</b>\n\nKerakli bo'limni tanlang:",
            reply_markup=admin_keyboard()
        )
    else:
        await message.answer("❌ Parol noto'g'ri! Qaytadan urinib ko'ring yoki /start bosing.")


@router.callback_query(F.data == "admin_players_count")
async def cb_players_count(call: CallbackQuery):
    if call.from_user.id != ADMIN_SUPPORT_ID:
        await call.answer("Taqiqlangan!", show_alert=True)
        return

    count = len(registered_users)
    await call.message.answer(f"📊 <b>Botdagi jami o'yinchilar soni:</b> {count} ta")
    await call.answer()


@router.callback_query(F.data == "admin_close")
async def cb_admin_close(call: CallbackQuery):
    await call.message.delete()
    await call.answer()


# =========================================================
# ADMIN SUPPORT AMALLARI
# =========================================================

@router.message(Command("admin_support"))
async def admin_support(message: Message, state: FSMContext):
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


# =========================================================
# USER SUPPORT XABARI
# =========================================================

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


# =========================================================
# ADMIN JAVOBI
# =========================================================

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
# RENDER UCHUN WEB SERVER
# =========================================================

async def start_web_server():
    app = web.Application()

    async def home(request):
        return web.Response(text="Viper Click Bot is running!")

    app.router.add_get("/", home)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


# =========================================================
# BOTNI ISHGA TUSHIRISH
# =========================================================

async def main():
    logging.basicConfig(level=logging.INFO)

    await start_web_server()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
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

    print("🔥 Viper Click Bot ishga tushdi!")
    print("🛠️ Admin Support faol!")
    print(f"👤 Admin ID: {ADMIN_SUPPORT_ID}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
