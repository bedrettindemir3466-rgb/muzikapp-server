@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "ID eksik"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0', # IPv6 çakışmalarını önlemek için
        'force_generic_extractor': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video linkini YouTube üzerinden alıyoruz
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # En temiz ses linkini seçiyoruz
            url = info.get('url')
            return jsonify({"url": url})
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return jsonify({"error": "Link alınamadı", "details": str(e)}), 500
