from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import urllib.parse

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET'])
def home():
    return "YouTube MP3 Backend tökéletesen működik! 🚀"

@app.route('/download', methods=['POST'])
def download_youtube_audio():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"status": "error", "message": "Nincs URL megadva!"}), 400
        
    url = data.get('url')
    print(f"\n🎵 Letöltés folyamatban: {url}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Itt olvassa be a sütiket
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(filename)[0] + ".mp3"
            title = info.get('title', 'Ismeretlen szám')

        print(f"✅ Sikeres letöltés: {title}")

        response = send_file(mp3_filename, mimetype="audio/mpeg", as_attachment=True)
        encoded_title = urllib.parse.quote(title)
        response.headers["X-Song-Title"] = encoded_title
        return response

    except Exception as e:
        print(f"❌ Hiba történt a letöltés során: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
