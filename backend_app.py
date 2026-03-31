import requests
import re
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SoundCloud yedek anahtarı (Dinamik bulma başarısız olursa devreye girer)
FALLBACK_ID = "iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"

def get_working_client_id():
    """SoundCloud'un güncel anahtarını JavaScript dosyalarından çeker."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get("https://soundcloud.com", headers=headers, timeout=5)
        scripts = re.findall(r'src="(https://a-v2.sndcdn.com/assets/[^"]+\.js)"', res.text)
        for url in reversed(scripts[:7]): # En güncel scriptleri tara
            js = requests.get(url, headers=headers, timeout=5).text
            match = re.search(r'client_id[:=]\s*"([a-zA-Z0-9]{32})"', js)
            if match: return match.group(1)
    except: pass
    return FALLBACK_ID

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    
    cid = get_working_client_id()
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # Arama sonuçlarını getir
        url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={cid}&limit=20"
        r = requests.get(url, headers=headers, timeout=10)
        
        if r.status_code != 200:
            return jsonify({"error": "SoundCloud erisim hatasi", "code": r.status_code}), 500

        data = r.json().get('collection', [])
        results = []
        host = request.host_url.rstrip('/')
        
        for item in data:
            results.append({
                "id": str(item['id']),
                "title": item.get('title', 'Bilinmeyen Şarkı'),
                "thumbnail": item.get('artwork_url') or item.get('user', {}).get('avatar_url') or "https://via.placeholder.com/150",
                "duration": f"{item.get('full_duration', 0) // 60000}:{(item.get('full_duration', 0) // 1000) % 60:02d}",
                "url": f"{host}/proxy_audio/{item['id']}" # Ses artık bizim üzerimizden akacak
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy_audio/<track_id>')
def proxy_audio(track_id):
    """Sesi SoundCloud'dan indirip kullanıcıya akıtarak 403 hatasını önler."""
    cid = get_working_client_id()
    try:
        # 1. Ham ses linkini al
        stream_api_url = f"https://api.soundcloud.com/tracks/{track_id}/stream?client_id={cid}"
        
        # 2. SoundCloud'un yönlendirdiği asıl dosyayı yakala
        r = requests.get(stream_api_url, stream=True, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
        
        # 3. Dosyayı parçalar halinde gönder (Bu kısım 403'ü bitiren kısımdır)
        def generate():
            for chunk in r.iter_content(chunk_size=1024 * 64):
                if chunk: yield chunk

        return Response(generate(), content_type=r.headers.get('Content-Type', 'audio/mpeg'))
    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    return "Muzik App Sunucusu Aktif ve Calisiyor!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
