import os
import fitz
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Optional: restrict to your Telegram user ID.
# Leave as 0 to allow everyone.
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

WATERMARK = "@THE_PHYSICS_LAD_BACKUP"
FONT_SIZE = 24
COLOR = (0.82, 0.82, 0.82)

app = Client(
    "watermark_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

def watermark_pdf(input_pdf: str, output_pdf: str):
    doc = fitz.open(input_pdf)

    for page in doc:
        rect = page.rect
        page.insert_text(
            (40, rect.height / 2),
            WATERMARK,
            fontsize=FONT_SIZE,
            color=COLOR,
            overlay=True,
        )

    doc.save(output_pdf)
    doc.close()

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    if OWNER_ID and message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ You are not authorized to use this bot.")
    await message.reply_text("📄 Send me a PDF and I'll return a watermarked copy.")

@app.on_message(filters.document)
async def pdf_handler(client: Client, message: Message):
    if OWNER_ID and message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ You are not authorized to use this bot.")

    doc = message.document
    if not doc.file_name.lower().endswith(".pdf"):
        return await message.reply_text("Please send a PDF file.")

    os.makedirs("/tmp/watermark", exist_ok=True)

    input_path = os.path.join("/tmp/watermark", doc.file_name)
    output_path = os.path.join("/tmp/watermark", "wm_" + doc.file_name)

    status = await message.reply_text("⬇️ Downloading PDF...")

    await message.download(file_name=input_path)

    await status.edit_text("💧 Adding watermark...")

    try:
        watermark_pdf(input_path, output_path)
    except Exception as e:
        await status.edit_text(f"❌ Error:\n{e}")
        return

    await status.edit_text("⬆️ Uploading...")

    await message.reply_document(
    document=output_path,
    file_name=doc.file_name,
    caption=message.caption or ""
)

    for p in (input_path, output_path):
        try:
            os.remove(p)
        except OSError:
            pass

    await status.delete()

print("Bot started...")
app.run()
