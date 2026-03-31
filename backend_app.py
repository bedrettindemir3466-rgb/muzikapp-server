import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_search import YoutubeSearch

# BU SATIR KRİTİK: Flask uygulamasını tanımlıyoruz
app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    try:
        results = YoutubeSearch(query, max_results=8).to_dict()
        formatted_results = []
        for res in results:
            formatted_results.append({
                "id": res['id'],
                "title": res['title'],
                "thumbnail": res['thumbnails'][0],
                "duration": res['duration']
            })
        return jsonify(formatted_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "ID eksik"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0',
        'force_generic_extractor': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            url = info.get('url')
            return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render portu için 10000 varsayılanını kullanırız
    app.run(host='0.0.0.0', port=10000)
