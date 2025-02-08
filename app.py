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
            'cookiefile': 'cookies.txt'  # Keep the cookies option
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Audio-only formats
            audio_formats = [
                {"format": f["format"], "url": f["url"]}
                for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"
            ]

            # Video and audio formats
            video_audio_formats = [
                {"format": f["format"], "url": f["url"]}
                for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") != "none"
            ]

            return jsonify({
                "audio_only_formats": audio_formats,
                "video_audio_formats": video_audio_formats
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
