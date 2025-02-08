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
        output_template = os.path.join(DOWNLOAD_FOLDER, unique_filename) + ".%(ext)s"
        
        ydl_opts = {
            'cookiefile': 'cookies.txt',
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_template,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegMerger',
            }]
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        merged_file = os.path.join(DOWNLOAD_FOLDER, f"{unique_filename}.mp4")
        
        # Ensure the merged file exists
        if not os.path.exists(merged_file):
            return jsonify({"error": "Merged MP4 file not found. Check if FFmpeg merged correctly."}), 500

        return jsonify({"download_url": f"{request.host_url}downloads/{unique_filename}.mp4"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
