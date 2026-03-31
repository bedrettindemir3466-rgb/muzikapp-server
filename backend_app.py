import requests
import re
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SoundCloud'un en stabil Client ID'lerinden biri (Yedek olarak tutuyoruz)
FALLBACK_ID = "iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"

def get_working_client_id():
    """Dinamik olarak çalışan bir ID bulmaya çalışır."""
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        # SoundCloud'un ana sayfasından güncel scriptleri çek
        res = requests.get("https://soundcloud.com", headers=headers, timeout=5)
        scripts = re.findall(r'src="(https://a-v2.sndcdn.com/assets/[^"]+\.js)"', res.text)
        for url in reversed(scripts):
            js = requests.get(url, headers=headers, timeout=5).text
            match = re.search(r'client_id[:=]\s*"([a-zA-Z0-9]{32})"', js)
            if match: return match.group(1)
    except: pass
    return FALLBACK_ID

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    
    client_id = get_working_client_id()
    try:
        # Arama API'sini mobil cihaz gibi çağırıyoruz (Daha az engel)
        search_url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={client_id}&limit=20"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            # Eğer 401 hatası alırsak yedek ID ile bir kez daha dene
            search_url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={FALLBACK_ID}&limit=20"
            response = requests.get(search_url, headers=headers, timeout=10)

        data = response.json().get('collection', [])
        results = []
        for item in data:
            results.append({
                "id": str(item['id']),
                "title": item.get('title', 'Bilinmeyen'),
                "thumbnail": item.get('artwork_url') or item.get('user', {}).get('avatar_url'),
                "duration": f"{item.get('full_duration', 0) // 60000}:{(item.get('full_duration', 0) // 1000) % 60:02d}",
                "url": f"{request.host_url}stream/{item['id']}" # Kendi sunucumuz üzerinden ses
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream/<track_id>')
def stream(track_id):
    client_id = get_working_client_id()
    # SoundCloud API üzerinden doğrudan MP3 yönlendirmesi
    stream_url = f"https://api.soundcloud.com/tracks/{track_id}/stream?client_id={client_id}"
    return redirect(stream_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
