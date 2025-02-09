from flask import Flask, request, send_file, jsonify
from yt_dlp import YoutubeDL
import os
import tempfile
import threading

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.getcwd(), 'cookies.txt')  # Path to cookies.txt

def cleanup_temp_dir(tmp_dir):
    """Delete temporary directory after a delay (ensure file is sent first)."""
    def delayed_cleanup():
        import time
        time.sleep(60)  # Wait 60 seconds before cleanup
        for root, dirs, files in os.walk(tmp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(tmp_dir)
    threading.Thread(target=delayed_cleanup).start()

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        # Create a persistent (non-context-managed) temp directory
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, "video.mp4")

        ydl_opts = {
            'cookiefile': COOKIES_PATH,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_path,  # Directly write to the output path
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

        # Send the file and schedule cleanup
        response = send_file(
            final_path,
            as_attachment=True,
            download_name=f"{info['title']}.mp4"
        )

        # Clean up after sending the file
        cleanup_temp_dir(tmp_dir)
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
