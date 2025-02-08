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
            'format': 'bestvideo+bestaudio/best',  # best video+audio
            'cookiefile': 'cookies.txt',
            'noplaylist': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Extract URLs for video+audio combined and audio-only
            video_audio_url = None
            audio_url = None

            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    video_audio_url = f['url']  # Best video+audio combined
                    break

            for f in info.get('formats', []):
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_url = f['url']  # Best audio-only
                    break

            return jsonify({
                "video_audio_url": video_audio_url,
                "audio_url": audio_url
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
