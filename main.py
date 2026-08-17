import asyncio
import io
import os
import logging
import qrcode
import cv2
import numpy as np
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Render'dagi Environment Variables bo'limida BOT_TOKEN borligini tekshiring.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start buyrug'i uchun
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "👋 **Salom! Men QR Kod generator va skaner botman.**\n\n"
        "• **Matn yoki ssilka yuboring** — QR kod yasab beraman.\n"
        "• **QR kod rasmini yuboring** — Ichidagi matnni o'qib beraman.",
        parse_mode="Markdown"
    )

# Matndan QR kod yaratish
@dp.message(F.text)
async def create_qr_handler(message: types.Message):
    qr_img = qrcode.make(message.text)
    
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    
    photo = BufferedInputFile(buffer.getvalue(), filename="qrcode.png")
    await message.answer_photo(photo, caption="✅ Sizning QR kodingiz tayyor!")

# Rasmdan QR kodni o'qish (OpenCV skaneri)
@dp.message(F.photo)
async def read_qr_handler(message: types.Message):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    # Rasmni OpenCV formati uchun tayyorlash
    file_bytes = np.frombuffer(downloaded_file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # OpenCV QR Code skaneri
    detector = cv2.QRCodeDetector()
    qr_data, _, _ = detector.detectAndDecode(img)
    
    if qr_data:
        await message.answer(
            f"🔍 **QR kod ichidagi ma'lumot:**\n\n`{qr_data}`",
            parse_mode="Markdown"
        )
    else:
        await message.answer("❌ Ushbu rasmdan QR kod topilmadi. Iltimos, aniqroq va tiniqroq rasm yuboring.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
