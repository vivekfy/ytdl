from flask import Response

def generate_file_chunks(file_path):
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            yield chunk

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

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = ydl.prepare_filename(info)

        response = Response(generate_file_chunks(final_path), content_type='video/mp4')
        response.headers['Content-Disposition'] = f'attachment; filename="{info["title"]}.mp4"'

        cleanup_temp_dir(tmp_dir)
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500
