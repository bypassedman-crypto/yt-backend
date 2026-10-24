from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import shutil
import tempfile
import traceback
import urllib.parse

app = Flask(__name__)
CORS(app, expose_headers=["X-Song-Title", "Content-Disposition"])


@app.route('/', methods=['GET'])
def home():
    return "YouTube MP3 Backend tökéletesen működik! 🚀"


@app.route('/download', methods=['POST'])
def download_youtube_audio():
    data = request.get_json(silent=True)
    if not data or 'url' not in data:
        return jsonify({"status": "error", "message": "Nincs URL megadva!"}), 400

    url = data['url']
    print(f"\n🎵 Letöltés folyamatban: {url}")

    tmp = tempfile.mkdtemp()
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tmp, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Ismeretlen szám')

        files = [f for f in os.listdir(tmp) if f.endswith('.mp3')]
        if not files:
            raise RuntimeError("Nem készült mp3 fájl (ffmpeg hiba?)")
        mp3_path = os.path.join(tmp, files[0])

        @after_this_request
        def cleanup(resp):
            shutil.rmtree(tmp, ignore_errors=True)
            return resp

        print(f"✅ Sikeres letöltés: {title}")
        response = send_file(
            mp3_path,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name=f"{files[0]}",
        )
        response.headers["X-Song-Title"] = urllib.parse.quote(title)
        return response

    except Exception as e:
        traceback.print_exc()
        shutil.rmtree(tmp, ignore_errors=True)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
