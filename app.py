from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
import os
from urllib.parse import unquote

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.getcwd(), 'cookies.txt')

@app.route('/download', methods=['GET'])
def get_video_url():
    # Decode the URL parameter to handle special characters
    url = unquote(request.args.get('url', ''))  # Use empty string as default
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    # Validate the URL format
    if "youtube.com/watch" not in url and "youtu.be/" not in url:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        ydl_opts = {
            'cookiefile': COOKIES_PATH,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']

        return jsonify({"video_url": video_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
