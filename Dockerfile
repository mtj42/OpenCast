
FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential

# To mount network share need cifs-utils
# RUN apt-get install -y cifs-utils 
# 
# Run Docker with mounted volume:
# https://stackoverflow.com/questions/23439126/how-to-mount-a-host-directory-in-a-docker-container
# $ docker run -it --env-file env.list --network host -v /tmp/winshare:/tmp/media opencast
# Mount, list, unmount in Ubuntu:
# mkdir /tmp/media
# sudo mount -t cifs -o username=guest //192.168.1.203/D /tmp/media
# df -hT
# sudo umount //192.168.1.203/D
# 
# For video processing:
# RUN apt-get install -y ffmpeg mkvtoolnix

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]


# To build:
# $ docker build -t opencast:lastest .
# Don't forget the trailing dot!

# To start/expose docker to same subnet:
# $ docker run -it --env-file env.list -p 192.168.1.153:8000:8000 opencast
