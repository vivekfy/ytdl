# Use a Python base image
FROM python:3.9-slim

# Install ffmpeg and dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install flask yt-dlp

# Run the app
CMD ["python", "main.py"]
