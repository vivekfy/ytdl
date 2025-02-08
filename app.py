from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Higher-quality video+audio
            'cookiefile': 'cookies.txt'
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            video_audio_url = None
            audio_only_url = None

            # Find video and audio URLs
            for f in info['formats']:
                if f['format_id'] == '18':  # Look for combined mp4 (if exists)
                    video_audio_url = f['url']
                elif f['vcodec'] == 'none' and f['acodec'] != 'none':
                    audio_only_url = f['url']

            return jsonify({
                "video_audio_url": video_audio_url or "Not available",
                "audio_only_url": audio_only_url or "Not available"
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
