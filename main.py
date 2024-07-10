import asyncio
import aiohttp
import os
from urllib.parse import urlparse
from pyrogram import Client, filters
from moviepy.editor import VideoFileClip
from tqdm.asyncio import tqdm
import direct

# Ganti dengan token API bot Anda
API_ID = "2345226"
API_HASH = "6cc6449dcef22f608af2cf7efb76c99d"
BOT_TOKEN = "5081813572:AAH4CJyx-Ub2Eh81pa94tRmuPnN4sMPusRc"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def download_file(url, session, save_dir, progress_callback):
    async with session.get(url) as response:
        response.raise_for_status()
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        save_path = os.path.join(save_dir, filename)
        
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024
        total_size_mb = total_size / (1024 * 1024)
        
        with open(save_path, 'wb') as f, tqdm(total=total_size_mb, unit='MB', unit_scale=True, desc=filename) as pbar:
            downloaded = 0
            last_updated = 0
            async for chunk in response.content.iter_chunked(chunk_size):
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                pbar.update(len(chunk) / (1024 * 1024))
                if downloaded - last_updated >= 10 * 1024 * 1024:  # Update every 10 MB
                    await progress_callback(downloaded / (1024 * 1024), total_size_mb)
                    last_updated = downloaded
            await progress_callback(downloaded / (1024 * 1024), total_size_mb)
        return save_path

def get_video_metadata(file_path):
    with VideoFileClip(file_path) as clip:
        duration = int(clip.duration)
        width, height = clip.size
        thumbnail_time = 5 * 60 + 21  # 5 menit 21 detik dalam detik
        if thumbnail_time > duration:  # Jika durasi video lebih pendek dari 5:21
            thumbnail_time = duration / 2  # Ambil tengah video sebagai thumbnail
        thumbnail_path = file_path + "_thumbnail.jpg"
        clip.save_frame(thumbnail_path, t=thumbnail_time)
        return duration, width, height, thumbnail_path

@app.on_message(filters.command("dl"))
async def download_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Harap kirimkan perintah dengan format: /dl <link>")
        return
    
    link = message.command[1]
    url = direct.direct_link_generator(link)
    save_dir = "dl"
    x = await message.reply_text("proses..")
    # Buat direktori jika belum ada
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    last_progress = None

    async with aiohttp.ClientSession() as session:
        async def progress_callback(current, total):
            nonlocal last_progress
            progress = f"Downloading: {current:.2f}/{total:.2f} MB"
            if progress != last_progress:
                await x.edit_text(progress)
                last_progress = progress

        save_path = await download_file(url, session, save_dir, progress_callback)
        try:
            duration, width, height, thumbnail_path = get_video_metadata(save_path)
            last_progress = None
            last_uploaded = 0
            async def upload_progress(current, total):
                nonlocal last_progress, last_uploaded
                if current - last_uploaded >= 10 * 1024 * 1024:  # Update every 10 MB
                    progress = f"Uploading: {current / (1024 * 1024):.2f}/{total / (1024 * 1024):.2f} MB"
                    if progress != last_progress:
                        await x.edit_text(progress)
                        last_progress = progress
                    last_uploaded = current
            
            await message.reply_video(
                save_path,
                duration=duration,
                width=width,
                height=height,
                thumb=thumbnail_path,
                progress=upload_progress
            )
        except Exception as e:
            await message.reply_text(f"Gagal mengirim video: {e}")
        finally:
            os.remove(save_path)  # Hapus file setelah dikirim
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)  # Hapus thumbnail setelah dikirim

print('bot aktif!!')
# Menjalankan bot
app.run()
