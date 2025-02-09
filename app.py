from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

COOKIES_PATH = os.path.join(os.getcwd(), 'cookies.txt')

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        ydl_opts = {
            'cookiefile': COOKIES_PATH,
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Sort formats by quality in descending order
            formats.sort(key=lambda x: -x.get('quality', 0))
            
            # Get top 3 video URLs
            video_urls = [f['url'] for f in formats[:3]]

        return jsonify({"video_urls": video_urls})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
