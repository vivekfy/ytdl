from flask import Flask, request, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return {"error": "Missing 'url' parameter"}, 400

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',  # Save video locally
            'cookiefile': 'cookies.txt'
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return send_file('video.mp4', as_attachment=True)

    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')  # Clean up after sending the file

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
