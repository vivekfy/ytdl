from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    
    try:
        # Fetch best video+audio and audio-only formats
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # best available
            'cookiefile': 'cookies.txt',
            'noplaylist': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Extract URLs for video+audio combined and audio-only
            video_audio_url = info['url'] if 'url' in info else None
            audio_url = next((f['url'] for f in info['formats'] if f['acodec'] != 'none' and f['vcodec'] == 'none'), None)

            return jsonify({
                "video_audio_url": video_audio_url,
                "audio_url": audio_url
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
