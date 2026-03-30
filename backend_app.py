from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch10:{query}", download=False)['entries']
            return jsonify([{
                'id': r['id'],
                'title': r['title'],
                'thumbnail': r['thumbnail'],
                'url': r['url']
            } for r in results])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {'format': 'bestaudio', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({'url': info['url']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
