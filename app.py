from flask import Flask, request, jsonify, send_from_directory
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)

# Directory to store downloaded files
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        video_filename = f"{uuid.uuid4()}.mp4"
        video_path = os.path.join(DOWNLOAD_FOLDER, video_filename)

        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': video_path,
            'merge_output_format': 'mp4'
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return jsonify({"download_url": f"{request.host_url}downloads/{video_filename}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
