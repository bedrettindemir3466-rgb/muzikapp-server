import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SoundCloud arama ve stream için public API kullanıyoruz
def get_soundcloud_stream(track_url):
    # Bu servis SoundCloud linkini doğrudan MP3'e çevirir
    api_url = f"https://api.soundclouddownloader.org/track?url={track_url}"
    try:
        return track_url # Bazı durumlarda direkt stream linki gerekir, 
        # ancak basitlik için SoundCloud'un kendi stream yapısını simüle edeceğiz.
    except: return None

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    try:
        # SoundCloud Public Search API
        search_url = f"https://api-v2.soundcloud.com/search?q={query}&client_id=iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I&limit=10"
        resp = requests.get(search_url)
        data = resp.json().get('collection', [])
        
        results = []
        for item in data:
            if item.get('kind') == 'track':
                results.append({
                    "id": str(item['id']),
                    "title": item['title'],
                    "thumbnail": item['artwork_url'] or item['user']['avatar_url'],
                    "duration": f"{item['duration'] // 60000}:{(item['duration'] // 1000) % 60:02d}",
                    "url": item['permalink_url'] # Tam sürüm linki
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    track_id = request.args.get('id')
    # SoundCloud stream linki oluşturma (ClientID bazen değişebilir)
    stream_url = f"https://api.soundcloud.com/tracks/{track_id}/stream?client_id=iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"
    return jsonify({"url": stream_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
