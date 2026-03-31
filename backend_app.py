import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_live_client_id():
    """SoundCloud ana sayfasından o anki geçerli Client ID'yi dinamik olarak çeker."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        # 1. Ana sayfayı ziyaret et
        response = requests.get("https://soundcloud.com", headers=headers, timeout=10)
        # 2. Sayfa içindeki tüm script (JS) dosyalarını bul
        script_urls = re.findall(r'src="(https://a-v2.sndcdn.com/assets/[^"]+\.js)"', response.text)
        
        # 3. JS dosyalarını tersten (genelde en güncel ID sondadır) tara
        for url in reversed(script_urls):
            js_content = requests.get(url, headers=headers, timeout=10).text
            # client_id:"XXXX" formatını yakala
            match = re.search(r'client_id[:=]\s*"([a-zA-Z0-9]{32})"', js_content)
            if match:
                print(f"Yeni Client ID Bulundu: {match.group(1)}")
                return match.group(1)
    except Exception as e:
        print(f"ID çekme hatası: {e}")
    
    # Eğer hata alırsan yedek ID (Bazen bu da çalışır)
    return "iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    try:
        # Her aramada veya belirli aralıklarla ID'yi tazele
        current_id = get_live_client_id()
        
        # SoundCloud Arama API v2
        search_url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={current_id}&limit=15"
        res = requests.get(search_url, timeout=10)
        data = res.json().get('collection', [])
        
        results = []
        for item in data:
            # Doğrudan çalınabilir stream linkini oluştur
            stream_url = f"https://api.soundcloud.com/tracks/{item['id']}/stream?client_id={current_id}"
            
            results.append({
                "id": str(item['id']),
                "title": item.get('title', 'Bilinmeyen Şarkı'),
                "thumbnail": item.get('artwork_url') or item.get('user', {}).get('avatar_url') or "https://via.placeholder.com/150",
                "duration": f"{item.get('full_duration', 0) // 60000}:{(item.get('full_duration', 0) // 1000) % 60:02d}",
                "url": stream_url
            })
        return jsonify(results)
    except Exception as e:
        print(f"Sistem Hatası: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Muzik App Backend Aktif - SoundCloud Altyapisi"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
