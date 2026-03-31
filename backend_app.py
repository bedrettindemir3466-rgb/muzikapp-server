import requests
import re
from flask import Flask, request, jsonify, Response, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

FALLBACK_ID = "iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"

def get_working_client_id():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get("https://soundcloud.com", headers=headers, timeout=5)
        scripts = re.findall(r'src="(https://a-v2.sndcdn.com/assets/[^"]+\.js)"', res.text)
        for url in reversed(scripts[:5]):
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
    try:
        url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={cid}&limit=15"
        r = requests.get(url, timeout=10)
        data = r.json().get('collection', [])
        results = []
        for item in data:
            # ÖNEMLİ: Linki tam URL olarak oluşturuyoruz
            proxy_url = f"{request.host_url.rstrip('/')}/proxy_audio/{item['id']}"
            results.append({
                "id": str(item['id']),
                "title": item.get('title', 'Bilinmeyen'),
                "thumbnail": item.get('artwork_url') or "https://via.placeholder.com/150",
                "duration": f"{item.get('full_duration', 0) // 60000}:{(item.get('full_duration', 0) // 1000) % 60:02d}",
                "url": proxy_url
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy_audio/<track_id>')
def proxy_audio(track_id):
    cid = get_working_client_id()
    try:
        # 1. Önce asıl stream URL'ini alıyoruz
        stream_api_url = f"https://api.soundcloud.com/tracks/{track_id}/stream?client_id={cid}"
        
        # 2. SoundCloud bizi asıl dosyaya yönlendirecek, o linki takip et (stream=True)
        r = requests.get(stream_api_url, stream=True, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0'})
        
        # 3. Dosyayı parçalar halinde kullanıcıya akıt (Proxy)
        return Response(r.iter_content(chunk_size=1024*1024), content_type=r.headers.get('Content-Type', 'audio/mpeg'))
    except Exception as e:
        return str(e), 500

@app.route('/')
def home():
    return "Muzik App Sunucusu Aktif!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
