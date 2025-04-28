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
    data = request.get_json()
    video_url = data.get('url')
    video_id = extract_video_id(video_url)
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id,
            proxies=PROXY  # Pass the proxy here
        )
        full_text = "\n".join(item['text'] for item in transcript_data)
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Summarize this podcast:"},
                {"role": "user", "content": full_text}
            ]
        )
        summary = completion.choices[0].message.content
        print(summary)
        return jsonify({'transcript': full_text, 'summary':summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def extract_video_id(url):
    import re
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

if __name__ == '__main__':
    app.run(debug=True)
