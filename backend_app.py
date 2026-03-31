import requests
import re
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SoundCloud yedek anahtarı
FALLBACK_ID = "iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"

def get_working_client_id():
    """Dinamik ID bulma - Daha fazla tarayıcı taklidi ile."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        # Ana sayfaya git
        res = requests.get("https://soundcloud.com", headers=headers, timeout=7)
        # JS dosyalarını bul
        scripts = re.findall(r'src="(https://a-v2.sndcdn.com/assets/[^"]+\.js)"', res.text)
        
        # En güncel 3 script dosyasını tara
        for url in reversed(scripts[:10]):
            try:
                js_content = requests.get(url, headers=headers, timeout=5).text
                match = re.search(r'client_id[:=]\s*"([a-zA-Z0-9]{32})"', js_content)
                if match:
                    return match.group(1)
            except:
                continue
    except Exception as e:
        print(f"ID çekme hatası: {e}")
    return FALLBACK_ID

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    
    cid = get_working_client_id()
    try:
        # API v2 kullanarak arama
        url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={cid}&limit=15"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        
        # Eğer SoundCloud 401 verirse yedek ID ile son bir kez dene
        if r.status_code != 200:
            url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={FALLBACK_ID}&limit=15"
            r = requests.get(url, headers=headers, timeout=10)

        data = r.json()
        collection = data.get('collection', [])
        
        results = []
        for item in collection:
            results.append({
                "id": str(item['id']),
                "title": item.get('title', 'Bilinmeyen'),
                "thumbnail": item.get('artwork_url') or item.get('user', {}).get('avatar_url') or "https://via.placeholder.com/150",
                "duration": f"{item.get('full_duration', 0) // 60000}:{(item.get('full_duration', 0) // 1000) % 60:02d}",
                "url": f"{request.host_url}stream/{item['id']}"
            })
        return jsonify(results)
    except Exception as e:
        # Hatanın ne olduğunu JSON olarak döndür ki App.js çökmesin
        return jsonify({"error": str(e), "details": "SoundCloud baglantisi kurulamadi"}), 500

@app.route('/stream/<track_id>')
def stream(track_id):
    cid = get_working_client_id()
    stream_url = f"https://api.soundcloud.com/tracks/{track_id}/stream?client_id={cid}"
    return redirect(stream_url)

@app.route('/')
def home():
    return "Sunucu Calisiyor!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
