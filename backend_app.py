@app.route('/play', methods=['GET'])
def play():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "ID eksik"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'source_address': '0.0.0.0',
        'force_generic_extractor': False,
        # Yeni eklenen kritik ayarlar:
        'nocheckcertificate': True,
        'extract_flat': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Linki alırken hata payını düşürmek için doğrudan URL oluşturuyoruz
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            url = info.get('url')
            if url:
                return jsonify({"url": url})
            else:
                return jsonify({"error": "Video linki ayıklanamadı"}), 404
    except Exception as e:
        print(f"Hata detayı: {str(e)}") # Render loglarında hatayı görmek için
        return jsonify({"error": str(e)}), 500
