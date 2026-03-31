import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_search import YoutubeSearch

app = Flask(__name__)
CORS(app)

# Güvenilir Invidious Sunucuları
INVIDIOUS_INSTANCES = [
    "https://inv.tux.pizza",
    "https://invidious.nerdvpn.de",
    "https://yewtu.be",
    "https://invidious.no-logs.com"
]

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])
    try:
        # Arama kısmında mevcut kütüphaneyi kullanmaya devam edebiliriz
        results = YoutubeSearch(query, max_results=10).to_dict()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "ID eksik"}), 400

    for instance in INVIDIOUS_INSTANCES:
        try:
            # Invidious API üzerinden video detaylarını sorgula
            api_url = f"{instance}/api/v1/videos/{video_id}"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # Sadece ses (audio) olan formatları filtrele
                audio_formats = [f for f in data.get('adaptiveFormats', []) if 'audio/' in f.get('type', '')]
                
                if audio_formats:
                    # En yüksek bit değerine sahip olanı (genellikle listenin sonu) seç
                    return jsonify({"url": audio_formats[-1]['url']})
        except Exception as e:
            print(f"{instance} sunucusu hata verdi, diğeri deneniyor...")
            continue

    return jsonify({"error": "Müzik linki hiçbir sunucudan alınamadı."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
