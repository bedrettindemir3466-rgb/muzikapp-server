from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from youtube_search import YoutubeSearch # Daha hafif ve hızlı arama

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    try:
        # yt-dlp yerine youtube_search kullanarak bot engelini aşıyoruz
        results = YoutubeSearch(query, max_results=10).to_dict()
        
        formatted_results = []
        for r in results:
            formatted_results.append({
                'id': r['id'],
                'title': r['title'],
                'thumbnail': r['thumbnails'][0] if r['thumbnails'] else "",
                'url': f"https://www.youtube.com/watch?v={r['id']}"
            })
        return jsonify(formatted_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Oynatma linki alırken bot engelini aşmak için alternatif 'format' ayarı
    ydl_opts = {
        'format': 'bestaudio/fastest', 
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0', # IPv6 çakışmalarını önlemek için
        'nocheckcertificate': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return jsonify({'url': info['url']})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)