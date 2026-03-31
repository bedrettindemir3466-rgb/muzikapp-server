import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Jamendo Client ID (Bu herkese açık bir test ID'sidir)
CLIENT_ID = "54ad1161"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    try:
        # Jamendo resmi API üzerinden arama yapıyoruz
        url = f"https://api.jamendo.com/v3.0/tracks/?client_id={CLIENT_ID}&format=jsonfull&limit=15&search={query}"
        response = requests.get(url, timeout=10)
        data = response.json().get('results', [])
        
        results = []
        for item in data:
            results.append({
                "id": item['id'],
                "title": item['name'] + " - " + item['artist_name'],
                "thumbnail": item['album_image'] or item['image'],
                "duration": f"{int(item['duration']) // 60}:{int(item['duration']) % 60:02d}",
                "url": item['audio'] # Doğrudan MP3 linki!
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Play rotasına gerek kalmadı çünkü URL zaten search'ten geliyor
@app.route('/play', methods=['GET'])
def play():
    track_url = request.args.get('url')
    return jsonify({"url": track_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
