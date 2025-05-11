#!/bin/bash

# Install ffmpeg
apt-get update && apt-get install -y ffmpeg

# Continue to app
pip install -r requirements.txt