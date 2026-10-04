"""
Viper Click Bot — /start va /help (aiogram 3.x)

O'rnatish:
    pip install -U aiogram aiohttp

Ishga tushirish:
    export BOT_TOKEN="123456:ABC..."          (Windows: set BOT_TOKEN=...)
    python viperclick_bot.py
"""

import asyncio
import logging
import os
from html import escape

from aiohttp import web  # Render portini ushlab turish uchun
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

# ============ SOZLAMALAR ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "8902470609:AAGbpTMFkQJwvulkSll3HCLjkOIckkoATa8")
MINIAPP_LINK = "https://t.me/ViperClickBot?startapp=ref_w2ng4fr9s2"  # mini app havolasi
MINIAPP_BASE = "https://t.me/ViperClickBot?startapp="
DEV_USERNAME = "Makhmudov_h001"                       # @ belgisiz
# ====================================

router = Router()


# ---------- MATNLAR ----------
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
        "<b>Viper Legend</b> darajasigacha ko'tarilib, reytingda yuqoriga chiqing! 🏆\n\n"
        "<b>Sizni nimalar kutmoqda:</b>\n"
        "⚡ <b>Tap-to-earn</b> — bosing, token ishlang. Zaryad o'zi tiklanadi\n"
        "📈 <b>Trading</b> — narx o'sadimi yoki tushadimi? To'g'ri topsangiz ×1.9\n"
        "🏢 <b>Biznes</b> — 10 ta biznesga investitsiya qiling\n"
        "🎲 <b>Qora quti</b> va 🗃 <b>Qutilar markazi</b> — tumorlar va sovrinlar\n"
        "🏦 <b>Bank</b> — kredit va depozit bilan balansni oshiring\n"
        "🎁 <b>Kunlik bonus</b> — har kuni kiring, 7 kunlik seriya oxirida katta sovg'a\n"
        "💌 <b>Sovg'a</b> — do'stingizga kod orqali token yuboring\n"
        "👥 <b>Do'stlar</b> — har bir taklif qilingan do'st uchun +200 token\n\n"
        "🎟 Promo kodingiz bormi? Uni <b>Bosh</b> sahifada kiriting.\n\n"
        "Boshlash uchun pastdagi tugmani bosing 👇"
    )


HELP_TEXT = (
    "❓ <b>Viper Click — yordam</b>\n\n"
    "<b>📱 Pastki menyu</b>\n"
    "🏠 <b>Bosh</b> — bosib token ishlash, kunlik bonus, promo kod, tumorlar\n"
    "🎲 <b>O'yin</b> — Ko'paytirish, Trading, Biznes, Qora quti, Qutilar markazi, Bank\n"
    "💌 <b>Sovg'a</b> — do'stga token yuborish va kelgan kodni kiritish\n"
    "🏆 <b>Reyting</b> — eng kuchli o'yinchilar ro'yxati\n"
    "👥 <b>Do'stlar</b> — shaxsiy havola va taklif qilinganlar soni\n\n"
    "<b>⚡ Token qanday ishlanadi?</b>\n"
    "Ekranga bosing — har bosishda token olasiz. Har bosish zaryad sarflaydi, "
    "zaryad esa har soniyada tiklanadi. Tumorlar va boostlar daromadni oshiradi.\n\n"
    "<b>🎮 O'yinlar</b>\n"
    "• O'yinlar balans <b>1000 token</b> ga yetganda ochiladi\n"
    "• <b>Trading</b> — har 12 soniyada yangi raund, yo'nalishni to'g'ri topsangiz ×1.9\n"
    "• <b>Biznes</b> — raund har 20 soniyada, natija barcha o'yinchilar uchun bir xil\n"
    "• <b>Qora quti</b> — 3 ta quti, kam tiksangiz yutish osonroq\n"
    "• <b>Bank</b> — kredit muddatida qaytarilmasa, balansdan ushlanadi. "
    "Depozitda ko'p tiksangiz foiz pastroq, muddat uzunroq\n\n"
    "<b>🎁 Bonuslar</b>\n"
    "• <b>Kunlik bonus</b> — 7 kun ketma-ket kiring, 7-kuni eng katta sovg'a\n"
    "• <b>Promo kod</b> — Bosh sahifada kiriting, bir marta ishlaydi\n"
    "• <b>Do'st taklif qilish</b> — har bir do'st uchun +200 token\n\n"
    "<b>🏅 Unvonlar</b>\n"
    "Balansingiz oshgani sari unvon ham o'sadi: "
    "🐣 Yangi o'yinchi → 🥉 Bronza → 🥈 Kumush → 🥇 Oltin → 💠 Platina → "
    "💎 Olmos → 👑 Usta → 🔥 Afsona → 🐍 Viper Legend → 🌟 O'lmas Viper\n\n"
    "<b>⚠️ Qoidalar</b>\n"
    "Avtoklikker yoki bot ishlatish taqiqlanadi. Aniqlansa, token jarima va "
    "<b>1 soatlik ban</b> beriladi. Halol o'ynang!\n\n"
    f"<b>📩 Aloqa:</b> muammo, savol yoki taklif bo'lsa @{DEV_USERNAME} ga yozing."
)


# ---------- TUGMALAR ----------
def start_keyboard(param: str | None = None) -> InlineKeyboardMarkup:
    link = f"{MINIAPP_BASE}{param}" if param else MINIAPP_LINK
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 O'ynash", url=link)],
            [InlineKeyboardButton(text="❓ Yordam", callback_data="help")],
        ]
    )


def help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎮 O'ynash", url=MINIAPP_LINK)],
            [InlineKeyboardButton(text="📩 Dasturchiga yozish", url=f"https://t.me/{DEV_USERNAME}")],
        ]
    )


# ---------- HANDLERLAR ----------
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    ref = command.args
    name = message.from_user.first_name if message.from_user else "do'st"
    await message.answer(
        start_text(name, referred=bool(ref)),
        reply_markup=start_keyboard(ref),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=help_keyboard())


@router.callback_query(F.data == "help")
async def cb_help(call: CallbackQuery):
    await call.message.answer(HELP_TEXT, reply_markup=help_keyboard())
    await call.answer()


# ---------- RENDER UCHUN SOXTA VEB-SERVER ----------
async def start_web_server():
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


# ---------- ISHGA TUSHIRISH ----------
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Render uchun veb-serverni parallel ishga tushiramiz
    await start_web_server()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="help", description="Yordam va qo'llanma"),
        ]
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
