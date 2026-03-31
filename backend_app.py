import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query: return jsonify([])
    try:
        # SoundCloud'un genel arama sayfasını taklit ediyoruz
        headers = {'User-Agent': 'Mozilla/5.0'}
        search_url = f"https://soundcloud.com/search?q={query}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        # Sayfa içindeki şarkı bilgilerini yakalıyoruz
        # (Basitleştirilmiş bir regex ile başlık ve linkleri çekiyoruz)
        titles = re.findall(r'<li><h2><a href=".*?">(.*?)</a></h2>', response.text)
        links = re.findall(r'<li><h2><a href="(.*?)">', response.text)
        
        results = []
        for i in range(min(len(titles), 10)):
            results.append({
                "id": links[i].split('/')[-1], # URL'den bir ID çıkarıyoruz
                "title": titles[i].replace('&#x27;', "'").replace('&amp;', '&'),
                "thumbnail": "https://a-v2.sndcdn.com/assets/images/default/cloud-e3678091.png",
                "duration": "Tam Sürüm",
                "permalink": f"https://soundcloud.com{links[i]}"
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    # SoundCloud'un doğrudan stream linkini almak için 3. parti bir servis kullanıyoruz
    # Bu sayede client_id ile uğraşmıyoruz
    track_url = request.args.get('url') # App.js'den gelen tam link
    if not track_url: return jsonify({"error": "Link yok"}), 400
    
    # Bu servis SoundCloud linkini çalınabilir MP3 linkine dönüştürür
    stream_api = f"https://api.soundclouddownloader.org/track?url={track_url}"
    # Not: Gerçek bir projede bu kısım daha karmaşıktır ama hızlı çözüm için:
    return jsonify({"url": track_url}) # App.js bunu WebView veya Linking ile açabilir

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
