import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SoundCloud Public Client ID (Bu ID değişebilir, en güncelidir)
CLIENT_ID = "iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    try:
        # Doğrudan SoundCloud üzerinden arama
        search_url = f"https://api-v2.soundcloud.com/search?q={query}&client_id={CLIENT_ID}&limit=10"
        response = requests.get(search_url, timeout=10)
        data = response.json().get('collection', [])
        
        results = []
        for item in data:
            if item.get('kind') == 'track':
                results.append({
                    "id": str(item['id']),
                    "title": item.get('title', 'Bilinmeyen Şarkı'),
                    "thumbnail": item.get('artwork_url') or item.get('user', {}).get('avatar_url'),
                    "duration": f"{item.get('duration', 0) // 60000}:{(item.get('duration', 0) // 1000) % 60:02d}"
                })
        return jsonify(results)
    except Exception as e:
        print(f"Arama Hatası: {str(e)}")
        return jsonify([])

@app.route('/play', methods=['GET'])
def play():
    track_id = request.args.get('id')
    if not track_id: return jsonify({"error": "ID yok"}), 400
    
    # SoundCloud stream URL'ini oluştur
    # Not: Bu URL doğrudan MP3 vermez, HLS stream verir. Mobil oyuncular bunu çalar.
    stream_url = f"https://api.soundcloud.com/tracks/{track_id}/stream?client_id={CLIENT_ID}"
    return jsonify({"url": stream_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
