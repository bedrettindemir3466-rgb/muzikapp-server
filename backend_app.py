from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import re
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app)

# SoundCloud API (key gerektirmez)
SOUNDCLOUD_API = "https://api-v2.soundcloud.com"

# SoundCloud'dan müzik ara
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query gerekli'}), 400
    
    try:
        # SoundCloud API - Doğrudan arama
        url = f"{SOUNDCLOUD_API}/search/tracks"
        params = {
            'q': query,
            'limit': 10,
            'offset': 0,
            'linked_partitioning': 1,
            'app_version': '1679091c5a880faf6fb5e6087eb1b2dc'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        songs = []
        if 'collection' in data:
            for track in data['collection'][:10]:
                if track.get('kind') == 'track' and track.get('streamable'):
                    songs.append({
                        'id': track.get('id'),
                        'title': track.get('title'),
                        'thumbnail': track.get('artwork_url', '').replace('-small.jpg', '-large.jpg'),
                        'duration': track.get('duration', 0) // 1000,  # MS to seconds
                        'artist': track.get('user', {}).get('username', 'Unknown'),
                        'url': track.get('permalink_url')
                    })
        
        return jsonify({'songs': songs})
    except Exception as e:
        return jsonify({'error': str(e), 'type': 'search_error'}), 500

# SoundCloud streaming linki al
@app.route('/stream/<int:track_id>')
def stream(track_id):
    try:
        # Track info'yu al
        url = f"{SOUNDCLOUD_API}/tracks/{track_id}"
        params = {
            'client_id': 'a3e059563d7fd3897001cceb82e5f6dc',
            'app_version': '1679091c5a880faf6fb5e6087eb1b2dc'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        track_data = response.json()
        
        # Progressive streaming URL
        if 'media' in track_data:
            for transcode in track_data['media'].get('transcodings', []):
                if 'progressive' in transcode.get('format', {}):
                    stream_url = transcode.get('url')
                    if stream_url:
                        # Stream URL'yi al (client_id ile)
                        stream_response = requests.get(
                            stream_url,
                            params={'client_id': 'a3e059563d7fd3897001cceb82e5f6dc'},
                            headers=headers,
                            timeout=10
                        )
                        stream_data = stream_response.json()
                        
                        return jsonify({
                            'url': stream_data.get('url'),
                            'title': track_data.get('title'),
                            'artist': track_data.get('user', {}).get('username', 'Unknown'),
                            'duration': track_data.get('duration', 0) // 1000
                        })
        
        # Fallback: HLS stream
        if 'media' in track_data:
            for transcode in track_data['media'].get('transcodings', []):
                if 'hls' in transcode.get('format', {}):
                    return jsonify({
                        'url': transcode.get('url') + '?client_id=a3e059563d7fd3897001cceb82e5f6dc',
                        'title': track_data.get('title'),
                        'artist': track_data.get('user', {}).get('username', 'Unknown'),
                        'duration': track_data.get('duration', 0) // 1000,
                        'format': 'hls'
                    })
        
        return jsonify({'error': 'Stream URL bulunamadı'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e), 'type': 'stream_error'}), 500

# Health check
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'soundcloud-streaming'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
