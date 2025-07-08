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
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that summarizes podcasts. "
                        "Return your summary as clean HTML: use <h2> for topics, <ul><li> for bullet points, and <b> for key terms. "
                        "No raw Markdown, no extra asterisks. No introductory or concluding paragraph."
                    )
                },
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

@app.route('/summarize_transcript', methods=['POST'])
def summarize_transcript():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON.'}), 400
    data = request.get_json(silent=True)
    transcript = data.get('transcript')
    if not transcript or not isinstance(transcript, list):
        return jsonify({'error': 'No transcript provided.'}), 400

    # Join the transcript into plain text (use your format!)
    full_text = "\n".join(
        seg['text'] if isinstance(seg, dict) and 'text' in seg else str(seg)
        for seg in transcript
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that summarizes podcasts. "
                        "Return your summary as clean HTML: use <h2> for topics, <ul><li> for bullet points, and <b> for key terms. "
                        "No raw Markdown, no extra asterisks. No introductory or concluding paragraph."
                    )
                },
                {"role": "user", "content": full_text}
            ]
        )
        summary = completion.choices[0].message.content
        return jsonify({'summary': summary})
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
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



import firebase_admin
from firebase_admin import auth as firebase_auth
import functools


firebase_admin.initialize_app()  # Uses ADC


def authenticate_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Missing token"}), 401
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"error": "Invalid token format"}), 401
        token = parts[1]
        try:
            decoded = firebase_auth.verify_id_token(token)
        except Exception as e:
            return jsonify({"error": "Invalid or expired token", "details": str(e)}), 403
        request.uid = decoded.get('uid')
        return func(*args, **kwargs)
    return wrapper



# @app.route('/feedback', methods=['POST'])
# def feedback():
#     data = request.get_json()
#     feedback_text = data.get('text', '').strip()
#     feedback_email = data.get('email', '').strip()
#     # Save to a file or database. Here, we'll append to a text file.
#     with open('feedback.txt', 'a', encoding='utf-8') as f:
#         f.write(f"Feedback: {feedback_text}\nEmail: {feedback_email}\n---\n")
#     return ('', 204)  # No Content



from firebase_admin import credentials, firestore
db = firestore.client()
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    feedback_text = data.get('text', '').strip()
    feedback_email = data.get('email', '').strip()
    
    # Basic validation
    if not feedback_text:
        return jsonify({'error': 'Feedback text required'}), 400

    # Save to Firestore
    doc_ref = db.collection('feedback').document()
    doc_ref.set({
        'text': feedback_text,
        'email': feedback_email,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    return ('', 204)  # No Content

@app.route('/save_summary', methods=['POST'])
@authenticate_token
def save_summary():
    user_id = request.uid
    data = request.get_json()
    summary_text = data.get('summary')
    doc_ref = firestore_client.collection('users').document(user_id).collection('history').document()
    doc_ref.set({
        'summary': summary_text,
        'created_at': firestore.SERVER_TIMESTAMP
    })
    return {"status": "ok", "id": doc_ref.id}, 200

# @app.route('/history', methods=['GET'])
# @authenticate_token
# def get_history():
#     user_id = request.uid
#     docs = firestore_client.collection('users').document(user_id).collection('history').stream()
#     history = [doc.to_dict() for doc in docs]
#     return jsonify(history), 200
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth as admin_auth, credentials, firestore

# ... (your Firebase init code)

@app.route('/history', methods=['GET'])
def get_history():
    id_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        decoded_token = admin_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        db = firestore.client()
        docs = db.collection('summaries').where('user_id', '==', uid).order_by('created_at', direction=firestore.Query.DESCENDING).limit(20).stream()
        history = []
        for doc in docs:
            data = doc.to_dict()
            history.append({
                'url': data.get('url'),
                'summary': data.get('summary', '')[:300] + "...", # Show preview
                'created_at': data.get('created_at').isoformat() if 'created_at' in data else ''
            })
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 401

if __name__ == '__main__':
    app.run(debug=True)
