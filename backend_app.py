import requests
import re
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_live_client_id():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get("https://soundcloud.com", headers=headers, timeout=5)
        js_urls = re.findall(r'src="(https://a-v2.sndcdn.com/assets/[^"]+\.js)"', res.text)
        for url in reversed(js_urls):
            js_res = requests.get(url, headers=headers, timeout=5)
            found = re.search(r'client_id[:=]\s*"([a-zA-Z0-9]{32})"', js_res.text)
            if found: return found.group(1)
    except: pass
    return "iZVscCksmSeUvS7Z6Y0mJJU8XN3mY28I"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    client_id = get_live_client_id()
    try:
        search_url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={client_id}&limit=15"
        data = requests.get(search_url, timeout=10).json().get('collection', [])
        results = []
        for item in data:
            # Uygulamanın sesi doğrudan çekebilmesi için sunucu üzerinden bir link veriyoruz
            stream_proxy_url = f"{request.host_url}stream/{item['id']}"
            results.append({
                "id": str(item['id']),
                "title": item.get('title', 'Bilinmeyen'),
                "thumbnail": item.get('artwork_url') or item.get('user', {}).get('avatar_url'),
                "duration": f"{item.get('full_duration', 0) // 60000}:{(item.get('full_duration', 0) // 1000) % 60:02d}",
                "url": stream_proxy_url # Proxy linki kullanıyoruz
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream/<track_id>')
def stream(track_id):
    # SoundCloud'dan gerçek MP3 linkini alıp oraya yönlendiriyoruz
    client_id = get_live_client_id()
    stream_url = f"https://api.soundcloud.com/tracks/{track_id}/stream?client_id={client_id}"
    return redirect(stream_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
