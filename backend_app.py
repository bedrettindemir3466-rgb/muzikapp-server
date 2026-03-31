from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# SoundCloud API Ayarları
SOUNDCLOUD_API = "https://api-v2.soundcloud.com"
CLIENT_ID = "a3e059563d7fd3897001cceb82e5f6dc" # En güncel ID

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        params = {'q': query, 'limit': 15, 'client_id': CLIENT_ID}
        
        response = requests.get(f"{SOUNDCLOUD_API}/search/tracks", params=params, headers=headers, timeout=10)
        data = response.json()
        
        results = []
        if 'collection' in data:
            for track in data['collection']:
                results.append({
                    'id': track.get('id'),
                    'title': track.get('title'),
                    'artist': track.get('user', {}).get('username', 'Bilinmeyen Sanatçı'),
                    'thumbnail': (track.get('artwork_url') or "").replace('-large.jpg', '-t500x500.jpg') or "https://via.placeholder.com/150",
                    'duration': f"{track.get('duration', 0) // 60000}:{(track.get('duration', 0) // 1000) % 60:02d}"
                })
        return jsonify(results) # Direkt liste döndürüyoruz
    except Exception as e:
        print(f"Hata: {e}")
        return jsonify([])

@app.route('/play', methods=['GET'])
def play():
    track_id = request.args.get('id')
    if not track_id: return jsonify({"error": "ID yok"}), 400
    try:
        params = {'client_id': CLIENT_ID}
        track_url = f"{SOUNDCLOUD_API}/tracks/{track_id}"
        response = requests.get(track_url, params=params, timeout=10).json()
        
        # Oynatılabilir stream linkini bulma
        for trans in response.get('media', {}).get('transcodings', []):
            if 'progressive' in trans.get('format', {}).get('protocol', ''):
                stream_data = requests.get(trans['url'], params=params).json()
                return jsonify({'url': stream_data.get('url')})
        
        # Fallback (HLS)
        hls_url = response['media']['transcodings'][0]['url']
        stream_data = requests.get(hls_url, params=params).json()
        return jsonify({'url': stream_data.get('url')})
    except:
        return jsonify({"error": "Çalma linki bulunamadı"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
