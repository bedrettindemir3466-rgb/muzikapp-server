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
        # YouTube yerine daha stabil bir arama motoru API'si kullanıyoruz
        search_url = f"https://api.deezer.com/search?q={query}&limit=10"
        response = requests.get(search_url, timeout=5)
        data = response.json().get('data', [])
        
        results = []
        for item in data:
            results.append({
                "id": str(item['id']),
                "title": f"{item['title']} - {item['artist']['name']}",
                "thumbnail": item['album']['cover_medium'],
                "duration": f"{item['duration'] // 60}:{item['duration'] % 60:02d}",
                "preview": item['preview'] # Doğrudan çalınabilir link
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    # Deezer verilerinde link zaten 'preview' içinde geliyor.
    # Bu route'u sadece frontend'deki mevcut yapın bozulmasın diye tutuyoruz.
    preview_url = request.args.get('url') # Frontend'den gelen preview url'i
    if preview_url:
        return jsonify({"url": preview_url})
    return jsonify({"error": "Link bulunamadı"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
