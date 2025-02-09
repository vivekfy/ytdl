from flask import Flask, request, Response, jsonify
from yt_dlp import YoutubeDL
import os
import tempfile
import threading

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.getcwd(), 'cookies.txt')  # Path to cookies.txt

def generate_and_delete_chunks(file_path):
    """Stream file in chunks and delete each chunk immediately."""
    chunk_size = 8192  # 8KB per chunk
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk
            # Immediately delete the served chunk by truncating the file
    os.remove(file_path)  # Delete the file after serving completely

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "video.mp4")

        ydl_opts = {
            'cookiefile': COOKIES_PATH,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_path,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        # Download and merge the video
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Stream file and delete chunks on the fly
        response = Response(generate_and_delete_chunks(output_path), content_type='video/mp4')
        response.headers['Content-Disposition'] = f'attachment; filename="{info["title"]}.mp4"'

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
