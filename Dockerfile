FROM python:3.10.8-slim-buster

# Install system dependencies
RUN apt update && \
    apt install -y git ffmpeg curl && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables to reduce output clutter
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /VJ-FILTER-BOT

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Start the bot
CMD ["python", "bot.py"]