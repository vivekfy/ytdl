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
        unique_filename = str(uuid.uuid4())
        download_base_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)

        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f"{download_base_path}.%(ext)s",
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegMerger'
            }]
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Ensure the merged MP4 file exists
        merged_file_path = f"{download_base_path}.mp4"
        if not os.path.exists(merged_file_path):
            return jsonify({"error": "Merged file not found"}), 500

        return jsonify({"download_url": f"{request.host_url}downloads/{unique_filename}.mp4"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
