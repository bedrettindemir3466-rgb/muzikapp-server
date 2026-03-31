from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

SOUNDCLOUD_API = "https://api-v2.soundcloud.com"
# En güncel ve çalışan Client ID
CLIENT_ID = "a3e059563d7fd3897001cceb82e5f6dc"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([]) # App.js hata almasın diye boş liste döndür
    
    try:
        url = f"{SOUNDCLOUD_API}/search/tracks"
        params = {
            'q': query,
            'limit': 15,
            'client_id': CLIENT_ID
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        songs = []
        if 'collection' in data:
            for track in data['collection']:
                songs.append({
                    'id': track.get('id'),
                    'title': track.get('title'),
                    'thumbnail': (track.get('artwork_url') or "").replace('-large.jpg', '-t500x500.jpg'),
                    'duration': f"{track.get('duration', 0) // 60000}:{(track.get('duration', 0) // 1000) % 60:02d}",
                    'artist': track.get('user', {}).get('username', 'Bilinmeyen')
                })
        return jsonify(songs) # Direkt listeyi gönderiyoruz, App.js bunu bekliyor
    except Exception as e:
        return jsonify([])

@app.route('/play', methods=['GET'])
def play():
    track_id = request.args.get('id')
    if not track_id: return jsonify({"error": "ID yok"}), 400
    try:
        url = f"{SOUNDCLOUD_API}/tracks/{track_id}"
        params = {'client_id': CLIENT_ID}
        response = requests.get(url, params=params, timeout=10).json()
        
        # Oynatılabilir URL'yi bul
        for transcode in response.get('media', {}).get('transcodings', []):
            if 'progressive' in transcode.get('format', {}).get('protocol', ''):
                stream_url = requests.get(transcode['url'], params=params).json()['url']
                return jsonify({'url': stream_url})
        
        # Eğer progressive yoksa HLS döndür
        hls_url = response['media']['transcodings'][0]['url']
        stream_url = requests.get(hls_url, params=params).json()['url']
        return jsonify({'url': stream_url})
    except:
        return jsonify({"error": "Link alınamadı"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
