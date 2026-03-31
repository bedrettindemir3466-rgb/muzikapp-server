from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch10', # 10 sonuç getir
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = []
            for entry in info['entries']:
                results.append({
                    'id': entry['id'],
                    'title': entry['title'],
                    'thumbnail': entry['thumbnail'],
                    'duration': f"{entry['duration'] // 60}:{entry['duration'] % 60:02d}",
                    'url': entry['webpage_url']
                })
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    video_url = request.args.get('url')
    if not video_url: return jsonify({"error": "URL yok"}), 400

    # YouTube'un engellemesini aşmak için en kritik ayarlar
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'force_generic_extractor': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # Tarayıcıda veya Expo Audio'da çalınabilir doğrudan .googlevideo linki
            return jsonify({'url': info['url']})
    except Exception as e:
        return jsonify({"error": "YouTube bu isteği engelledi, lütfen tekrar deneyin."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
