import yt_dlp
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# GitHub'daki çerez dosyan
COOKIES_FILE = 'cookies.txt'

def get_ydl_opts():
    return {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = []
            host = request.host_url.rstrip('/')
            
            for entry in info.get('entries', []):
                if not entry: continue
                results.append({
                    "id": entry.get('id'),
                    "title": entry.get('title'),
                    "thumbnail": entry.get('thumbnails')[0]['url'] if entry.get('thumbnails') else "",
                    "duration": f"{entry.get('duration', 0) // 60}:{entry.get('duration', 0) % 60:02d}",
                    "url": f"{host}/proxy_stream/{entry.get('id')}"
                })
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy_stream/<video_id>')
def proxy_stream(video_id):
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            url = info['url']
            
            # YouTube'dan gelen ham veriyi çekip kullanıcıya akıtıyoruz
            r = requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
            
            def generate():
                for chunk in r.iter_content(chunk_size=1024*128):
                    if chunk: yield chunk
            
            return Response(generate(), content_type="audio/mpeg")
    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    return "YouTube Proxy Aktif ve Hazir!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
