FROM ubuntu:20.04
RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y libx11-dev libpthread-stubs0-dev libfftw3-dev libiio-dev netcat python3-dev python3-pip xxd mplayer okteta
ADD leandvb.tar.gz /usr/bin
COPY tsduck.deb /tmp/tsduck.deb
RUN apt-get install -y /tmp/tsduck.deb
RUN chmod +X /usr/bin
RUN pip3 install kaitaistruct
