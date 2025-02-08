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
            'format': 'best',
            'cookiefile': 'cookies.txt'  # Add this line
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"url": info['url']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
