# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Gradio default port (GRADIO_SERVER_PORT)
EXPOSE 7860

# Remove GRADIO_SERVER_NAME and GRADIO_SERVER_PORT from here

# Run the app
CMD ["python", "app.py"] 