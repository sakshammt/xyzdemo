from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

def get_audio_url(youtube_url):
    """Extract audio URL from YouTube video"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return {
            'url': info['url'],
            'title': info.get('title', 'Unknown'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration', 0),
            'author': info.get('uploader', 'Unknown')
        }

@app.route('/api/audio', methods=['POST'])
def get_audio():
    """API endpoint to get audio info"""
    try:
        data = request.json
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        audio_info = get_audio_url(youtube_url)
        return jsonify(audio_info)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream', methods=['GET'])
def stream_audio():
    """Stream audio to bypass CORS issues"""
    audio_url = request.args.get('url')
    
    if not audio_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    def generate():
        with requests.get(audio_url, stream=True) as r:
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk
    
    return Response(generate(), mimetype='audio/webm')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
