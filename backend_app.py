import yt_dlp
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# GitHub'a yüklediğin çerez dosyasının adı
COOKIES_FILE = 'cookies.txt'

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    
    # YouTube'u çerezlerle kandırma ayarları
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
        'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube'da 10 sonuçluk arama yap
            search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = []
            host = request.host_url.rstrip('/')
            
            for entry in search_results.get('entries', []):
                if not entry: continue
                results.append({
                    "id": entry.get('id'),
                    "title": entry.get('title'),
                    "thumbnail": entry.get('thumbnails')[0]['url'] if entry.get('thumbnails') else "",
                    "duration": f"{entry.get('duration', 0) // 60}:{entry.get('duration', 0) % 60:02d}",
                    "url": f"{host}/stream/{entry.get('id')}"
                })
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e), "msg": "Çerezler geçersiz veya YouTube yine engelledi"}), 500

@app.route('/stream/<video_id>')
def stream(video_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # YouTube'un verdiği gerçek ses linkine yönlendiriyoruz
            return redirect(info['url'])
    except Exception as e:
        return f"Oynatma Hatası: {str(e)}", 403

@app.route('/')
def home():
    return "Müzik Uygulaması (Cookies Aktif) Çalışıyor!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
