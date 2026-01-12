from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid
import logging

# -----------------------
# Logging configuration
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------
# Flask app
# -----------------------
app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
logger.info(f"Download directory ready: {DOWNLOAD_DIR}")

# -----------------------
# Routes
# -----------------------
@app.route("/download-mp3", methods=["POST"])
def download_mp3():
    logger.info("Received /download-mp3 request")

    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "YouTube URL is required"}), 400

    youtube_url = data["url"]

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "ffmpeg_location": r"L:\Youtubedownloader\ffmpeg-2025-12-31-git-38e89fe502-essentials_build\bin",
        "windowsfilenames": True,
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    try:
        logger.info("Starting yt-dlp download...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)

        title = info["title"]
        mp3_path = os.path.join(DOWNLOAD_DIR, f"{title}.mp3")

        logger.info(f"Expected MP3 path: {mp3_path}")

        if not os.path.exists(mp3_path):
            logger.error("MP3 file not found after download")
            return jsonify({"error": "MP3 conversion failed"}), 500

        logger.info("MP3 download completed successfully")

        return send_file(
            mp3_path,
            as_attachment=True,
            download_name=f"{title}.mp3"
        )

    except Exception as e:
        logger.exception("Download failed")
        return jsonify({"error": str(e)}), 500

# -----------------------
# Entry point
# -----------------------
if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )