import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_search import YoutubeSearch

app = Flask(__name__)
CORS(app)

# Daha stabil ve hızlı Invidious sunucuları
INVIDIOUS_INSTANCES = [
    "https://invidious.flokinet.to",
    "https://inv.nand.one",
    "https://invidious.vpsfree.cz",
    "https://invidious.sethforprivacy.com",
    "https://inv.riverside.rocks"
]

@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "ID eksik"}), 400

    for instance in INVIDIOUS_INSTANCES:
        try:
            print(f"Deneniyor: {instance}") # Loglarda hangi sunucunun denendiğini görürsün
            api_url = f"{instance}/api/v1/videos/{video_id}"
            response = requests.get(api_url, timeout=4) # Timeout süresini 4 saniye yaptık
            
            if response.status_code == 200:
                data = response.json()
                # adaptiveFormats içindeki ses dosyalarını al
                audio_streams = [s for s in data.get('adaptiveFormats', []) if 'audio/' in s.get('type', '')]
                
                if audio_streams:
                    # En sonuncu (genellikle en yüksek kaliteli) stream'i döndür
                    return jsonify({"url": audio_streams[-1]['url']})
        except Exception as e:
            print(f"{instance} hatası: {str(e)}")
            continue

    return jsonify({"error": "Müzik linki bulunamadı. Lütfen tekrar deneyin."}), 404

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    try:
        results = YoutubeSearch(query, max_results=10).to_dict()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
