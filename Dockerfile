FROM ubuntu:trusty

MAINTAINER levy levylll@163.com

# Set Locale

RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8



# Enable Universe and Multiverse and install dependencies.

RUN echo deb http://archive.ubuntu.com/ubuntu precise universe multiverse >> /etc/apt/sources.list; \
    apt-get update; \
    apt-get -y install autoconf automake build-essential git mercurial cmake libass-dev libgpac-dev libtheora-dev libtool libvdpau-dev libvorbis-dev pkg-config texi2html zlib1g-dev libmp3lame-dev wget yasm openssl libssl-dev; \
    apt-get clean; \
    apt-get -y install libxcb-shm0; \
    apt-get -y install libxcb-xfixes0; \
    apt-get -y install libasound2

# Run build script

COPY program /program
WORKDIR /program
RUN /sbin/ldconfig -v
#ADD script/build.sh /build.sh
#RUN ["/bin/bash", "/build.sh"]
#RUN python py/transcode.py /program/zhz-L4.mp4 gaoqing all > tx.log 2>&1

#CMD ["/bin/bash"]
