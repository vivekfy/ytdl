import os
import uuid
from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        # Unique file names to avoid conflicts
        video_file = f"{uuid.uuid4()}.mp4"
        audio_file = f"{uuid.uuid4()}.mp3"
        output_file = f"{uuid.uuid4()}.mp4"

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': {'video': video_file, 'audio': audio_file},
            'merge_output_format': 'mp4'
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Check if FFmpeg is available
        if not os.system("ffmpeg -version") == 0:
            return jsonify({"error": "FFmpeg not found. Please install FFmpeg."}), 500

        # Merge video and audio using FFmpeg
        os.system(f"ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}")

        # Clean up the separate files
        os.remove(video_file)
        os.remove(audio_file)

        return send_file(output_file, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
