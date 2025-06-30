# SummarizePodcast

## 🚀 Summarize YouTube

This application fetches a YouTube transcript, summarizes it via the OpenAI API, and serves it as a Cloud Run service.

---

## 📋 Table of Contents
- [Prerequisites](#-prerequisites)
- [Build & Deploy](#-build--deploy)
- [Sample .env File](#-sample-env-file)

---

## ✅ Prerequisites

- `app.py` (Flask application)
- `requirements.txt` listing:
  - Flask
  - Gunicorn
  - youtube-transcript-api
  - openai
  - etc.
- `.env` file with required environment variables (see below)
- Docker installed
- Google Cloud SDK (`gcloud`) installed and initialized
- Billing enabled on your Google Cloud project

---

## 🗂️ Sample .env File

```
OPENAI_API_KEY=your_openai_api_key_here
PROXY_CREDS=your_proxy_creds_here
```

---

## 📦 Build & Deploy

### 1. Enable Necessary Google Cloud Services

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

### 2. Create Artifact Registry (One-Time Setup)

```bash
gcloud artifacts repositories create summarize-repo \
  --repository-format=docker \
  --location=us-central1
```

### 3. Build and Tag Your Docker Image

- To see project names:

```bash
gcloud projects list
```

- Build images:

```bash
docker build -t us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube .
docker build -t summarize-youtube .
```

#### 3.1 Run and Test App Locally

```bash
docker run -p 8080:8080 --env-file .env summarize-youtube
```

#### 3.2 Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project PROJECT_ID
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 4. Push the Image

```bash
docker push us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube
```

### 5. Deploy to Cloud Run

```bash
gcloud run deploy summarize-youtube \
  --image=us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=$env:OPENAI_API_KEY,PROXY_CREDS=$env:PROXY_CREDS"
```

**One-line deploy:**

```bash
gcloud run deploy summarize-youtube --image=us-central1-docker.pkg.dev/summarizepodcast/summarize-repo/summarize-youtube --platform=managed --region=us-central1 --allow-unauthenticated --set-env-vars="OPENAI_API_KEY=$env:OPENAI_API_KEY,PROXY_CREDS=$env:PROXY_CREDS"
```

---
