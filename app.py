from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from openai import OpenAI

from dotenv import load_dotenv
import os
load_dotenv()
PROXY_CREDS = os.getenv('PROXY_CREDS')

app = Flask(__name__)

# Setup your proxy config
PROXY = {
    "http": f"http://{PROXY_CREDS}@p.webshare.io:80",
    "https": f"http://{PROXY_CREDS}@p.webshare.io:80"
}
# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Input validation
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON.'}), 400
    data = request.get_json(silent=True)
    if not data or 'url' not in data or not data['url']:
        return jsonify({'error': 'No URL provided.'}), 400
    video_url = data['url']
    try:
        video_id = extract_video_id(video_url)
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id,
            proxies=PROXY  # Pass the proxy here
        )
        full_text = "\n".join(item['text'] for item in transcript_data)
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Summarize this podcast:"},
                {"role": "user", "content": full_text}
            ]
        )
        summary = completion.choices[0].message.content
        print(summary)
        return jsonify({'transcript': full_text, 'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    import re
    # Handles various YouTube URL formats
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    raise ValueError('Invalid YouTube URL.')

if __name__ == '__main__':
    app.run(debug=True)
