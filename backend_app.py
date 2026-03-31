import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_search import YoutubeSearch

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    try:
        results = YoutubeSearch(query, max_results=10).to_dict()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "ID eksik"}), 400

    # YOUTUBE ENGELİNİ AŞAN GÜNCEL AYARLAR
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # YouTube'u kandırmak için Android istemcisi kullanıyoruz
        'user_agent': 'Mozilla/5.0 (Android 12; Mobile; rv:94.0) Gecko/94.0 Firefox/94.0',
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'skip': ['dash', 'hls']
            }
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video URL'sini doğrudan işliyoruz
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Bazı durumlarda 'url' yerine 'formats' içinden en iyisini seçmek gerekebilir
            url = info.get('url')
            if not url and 'formats' in info:
                url = info['formats'][0]['url']
                
            if url:
                return jsonify({"url": url})
            else:
                return jsonify({"error": "Video linki bulunamadı"}), 404
                
    except Exception as e:
        # Hatayı Render loglarında görebilmek için yazdırıyoruz
        print(f"Hata detayı: {str(e)}") 
        return jsonify({"error": "YouTube isteği reddetti"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
