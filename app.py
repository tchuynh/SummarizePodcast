from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from openai import OpenAI

from dotenv import load_dotenv
import os, json

load_dotenv()
PROXY_CREDS = os.getenv('PROXY_CREDS')

app = Flask(__name__)

PROXY = {
    "http": f"http://{PROXY_CREDS}@p.webshare.io:80",
    "https": f"http://{PROXY_CREDS}@p.webshare.io:80"
}
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON.'}), 400
    data = request.get_json(silent=True)
    if not data or 'url' not in data or not data['url']:
        return jsonify({'error': 'No URL provided.'}), 400
    video_url = data['url']
    try:
        video_id = extract_video_id(video_url)
        cache_path = os.path.join(DATA_DIR, f"{video_id}.json")

        # Check cache first!
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return jsonify(saved)

        # Otherwise, fetch transcript
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id,
            proxies=PROXY
        )
        # Save transcript as a list of dicts [{start, text}]
        transcript = [
            {'start': seg['start'], 'text': seg['text']} for seg in transcript_data
        ]
        # For summary, just pass plain transcript text
        full_text = "\n".join(seg['text'] for seg in transcript)
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Summarize this podcast:"},
                {"role": "user", "content": full_text}
            ]
        )
        summary = completion.choices[0].message.content

        result = {'transcript': transcript, 'summary': summary}
        # Save to cache!
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(result, f)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
from flask import render_template

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

def extract_video_id(url):
    import re
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    raise ValueError('Invalid YouTube URL.')

from flask import send_from_directory

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml', mimetype='application/xml')
from flask import send_from_directory

@app.route('/google982f50214a0c928e.html')
def google_verification():
    return send_from_directory('.', 'google982f50214a0c928e.html')

@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt', mimetype='text/plain')
    
@app.route('/blog')
def blog():
    return render_template('blog_index.html')

@app.route('/blog/how-to-get-a-youtube-transcript-instantly')
def blog_transcript():
    return render_template('blog_transcript.html')

@app.route('/blog/5-ways-to-summarize-podcasts-with-ai')
def blog_podcast_ai():
    return render_template('blog_podcast_ai.html')

@app.route('/blog/top-youtube-channels-for-learning')
def blog_youtube_learning():
    return render_template('blog_youtube_learning.html')

if __name__ == '__main__':
    app.run(debug=True)
