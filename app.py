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
            'cookiefile': 'cookies.txt'  # Keep cookies to handle restricted videos
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Get audio-only formats
            audio_formats = [
                {"format_id": f["format_id"], "ext": f["ext"], "url": f["url"]}
                for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") == "none"
            ]

            # Get video+audio formats sorted by resolution
            video_audio_formats = sorted(
                [
                    {"format_id": f["format_id"], "resolution": f.get("resolution", "N/A"),
                     "ext": f["ext"], "url": f["url"]}
                    for f in info["formats"] if f.get("acodec") != "none" and f.get("vcodec") != "none"
                ],
                key=lambda x: x.get("resolution", "N/A"), reverse=True
            )

            return jsonify({
                "audio_only_formats": audio_formats,
                "video_audio_formats": video_audio_formats
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
