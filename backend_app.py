import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_search import YoutubeSearch

app = Flask(__name__)
CORS(app)

@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "ID eksik"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # YouTube'un veri merkezi engellerini aşmak için en kritik ayar:
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
                'skip': ['dash', 'hls']
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.10.35 (Linux; U; Android 11) gzip',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            url = info.get('url')
            if url:
                return jsonify({"url": url}) # Bu artık şarkının tam sürümüdür
            return jsonify({"error": "Link alınamadı"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    try:
        results = YoutubeSearch(query, max_results=10).to_dict()
        return jsonify(results)
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
