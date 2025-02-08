from flask import Flask, request, Response, jsonify
from yt_dlp import YoutubeDL
import os
import tempfile

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.getcwd(), 'cookies.txt')

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        # Create a temporary directory
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
            final_path = ydl.prepare_filename(info)

        # Stream the file in chunks
        def generate():
            with open(final_path, 'rb') as f:
                while chunk := f.read(1024 * 1024):  # Read 1MB chunks
                    yield chunk
            # Cleanup after streaming
            os.remove(final_path)
            os.rmdir(tmp_dir)

        return Response(
            generate(),
            headers={
                'Content-Disposition': f'attachment; filename="{info["title"]}.mp4"',
                'Content-Type': 'video/mp4'
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
