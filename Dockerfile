# Use official Python base image
FROM python:3.13-slim

# Create working directory
WORKDIR /app

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Start the app with Gunicorn
# CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8080} app:app"]
CMD ["gunicorn", "-b", ":8080", "app:app"]