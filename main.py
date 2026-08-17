import asyncio
import io
import os
import logging
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8728752369:AAFHwOh0OoKKT-hp6l2TA9zA2Hfmo1TL65k")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start buyrug'i uchun
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "Salom! Men QR Kod generator va skaner botman.\n\n"
        "• Matn yoki ssilka yuboring — **QR kod yasab beraman**\n"
        "• QR kod rasmini yuboring — **Ichidagi matnni o'qib beraman**"
    )

# Matndan QR kod yaratish
@dp.message(F.text)
async def create_qr_handler(message: types.Message):
    qr_img = qrcode.make(message.text)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    
    photo = BufferedInputFile(buffer.getvalue(), filename="qrcode.png")
    await message.answer_photo(photo, caption="Sizning QR kodingiz ready!")

# Rasmdan QR kodni o'qish (Skaner)
@dp.message(F.photo)
async def read_qr_handler(message: types.Message):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    image = Image.open(downloaded_file)
    decoded_objects = decode(image)
    
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode('utf-8')
        await message.answer(f"🔍 **QR kod ichidagi ma'lumot:**\n\n`{qr_data}`", parse_mode="Markdown")
    else:
        await message.answer("❌ Ushbu rasmdan QR kod topilmadi. Iltimos, aniqroq rasm yuboring.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
