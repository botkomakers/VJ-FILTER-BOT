# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

FROM python:3.10.8-slim-buster

# Update and install necessary dependencies
RUN apt update && apt upgrade -y
RUN apt install -y git ffmpeg  # Install ffmpeg along with git

# Copy the requirements file
COPY requirements.txt /requirements.txt

# Install pip dependencies
RUN pip3 install -U pip && pip3 install -U -r /requirements.txt

# Create the working directory and set it as the working directory
RUN mkdir /VJ-FILTER-BOT
WORKDIR /VJ-FILTER-BOT

# Copy the rest of your application code
COPY . /VJ-FILTER-BOT

# Command to run the bot
CMD ["python", "bot.py"]