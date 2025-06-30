# SummarizePodcast

# 🚀 Summarize YouTube

This application fetches a YouTube transcript, summarizes it via the OpenAI API, and serves it as a Cloud Run service.

---

## ✅ Prerequisites

- `app.py` (Flask application)
- `requirements.txt` listing Flask, Gunicorn, youtube-transcript-api, openai, etc.
- `.env` file with:
- Docker installed  
- Google Cloud SDK (`gcloud`) installed and initialized  
- Billing enabled on your Google Cloud project  

---

## 📦 Build & Deploy

1. Enable necessary services

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

2. Create Artifact Registry (one-time setup)
gcloud artifacts repositories create summarize-repo \
  --repository-format=docker --location=us-central1

3. Build and tag your Docker image
# to see project names 
gcloud projects list 
docker build -t us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube .
docker build -t summarize-youtube .

3.1 run and test app

docker run -p 8080:8080 summarize-youtube

docker run -p 8080:8080 --env-file .env summarize-youtube

docker run -p 8080:8080 --env-file ../../.env summarize-youtube


3.2 login
gcloud auth login

gcloud config set project PROJECT_ID

gcloud auth configure-docker us-central1-docker.pkg.dev


4. Push the image
docker push us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube

5. Deploy to Cloud Run
gcloud run deploy summarize-youtube `
  --image=us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube `
  --platform=managed `
  --region=us-central1 `
  --allow-unauthenticated `
  --set-env-vars="OPENAI_API_KEY=$env:OPENAI_API_KEY,PROXY_CREDS=$env:PROXY_CREDS"


one line
gcloud run deploy summarize-youtube --image=us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube --platform=managed --region=us-central1 --allow-unauthenticated --set-env-vars="OPENAI_API_KEY=$env:OPENAI_API_KEY,PROXY_CREDS=$env:PROXY_CREDS"

