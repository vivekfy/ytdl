from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route('/video_info', methods=['GET'])
def video_info():
    url = request.args.get('url')
    if not url:
        return {"error": "Missing 'url' parameter"}, 400

    try:
        ydl_opts = {
            'noplaylist': True,
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [{
                "format_id": f["format_id"],
                "resolution": f.get("resolution", "audio-only" if "audio" in f["format"] else "unknown"),
                "file_size": f.get("filesize", "unknown"),
                "ext": f.get("ext"),
            } for f in info['formats'] if f.get('url')]

            return jsonify({
                "title": info.get('title', 'unknown'),
                "formats": formats
            })
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    format_id = request.args.get('format_id')
    if not url or not format_id:
        return {"error": "Missing 'url' or 'format_id' parameter"}, 400

    filename = ''
    try:
        ydl_opts = {
            'format': format_id,
            'outtmpl': '%(title)s.%(ext)s',  # Save as original title
            'cookiefile': 'cookies.txt'
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Ensure filename cleanup only if it exists
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as cleanup_error:
                print(f"Error cleaning up file: {cleanup_error}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
