import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    try:
        # SoundCloud'un resmi widget arama API'si (Anahtar gerektirmez)
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://api-v2.soundcloud.com/search/queries?q={query}&client_id=iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I&limit=10"
        
        # Gerçek arama sonuçlarını alıyoruz
        search_url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id=iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I&limit=10"
        response = requests.get(search_url, headers=headers, timeout=10)
        data = response.json().get('collection', [])
        
        results = []
        for item in data:
            results.append({
                "id": item['id'],
                "title": item['title'],
                "thumbnail": item['artwork_url'] or item.get('user', {}).get('avatar_url'),
                "duration": f"{item['duration'] // 60000}:{(item['duration'] // 1000) % 60:02d}",
                "url": f"https://api.soundcloud.com/tracks/{item['id']}/stream?client_id=iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    track_url = request.args.get('url')
    return jsonify({"url": track_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
