import yt_dlp
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Render'da geçici dosya depolama alanı
DOWNLOAD_PATH = "/tmp"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True, # Hızlı arama için sadece meta veriyi al
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube'da arama yap
            search_results = ydl.extract_info(f"ytsearch15:{query}", download=False)
            results = []
            
            for entry in search_results.get('entries', []):
                if not entry: continue
                results.append({
                    "id": entry.get('id'),
                    "title": entry.get('title'),
                    "thumbnail": entry.get('thumbnails')[0]['url'] if entry.get('thumbnails') else "",
                    "duration": f"{entry.get('duration', 0) // 60}:{entry.get('duration', 0) % 60:02d}",
                    "url": f"{request.host_url.rstrip('/')}/stream/{entry.get('id')}"
                })
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream/<video_id>')
def stream(video_id):
    """Video ID'sini kullanarak doğrudan ses linkine yönlendirir."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'force_generic_extractor': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # YouTube'un verdiği ham ses linkine (URL) yönlendir
            return redirect(info['url'])
    except Exception as e:
        # Eğer bot engeline takılırsa 403 hatası verecektir
        return f"YouTube Engeli: {str(e)}", 403

if __name__ == '__main__':
    # Render için port ayarı
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
