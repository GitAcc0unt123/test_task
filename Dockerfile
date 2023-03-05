FROM python
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y &&\
    pip3 install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir /app/test_frames
