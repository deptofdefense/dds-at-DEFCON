FROM ubuntu:20.04
ADD leandvb.tar.gz /usr/bin
RUN apt-get update
RUN chmod +X /usr/bin
RUN apt-get install -y libx11-dev libpthread-stubs0-dev libfftw3-dev libiio-dev netcat
ADD start_broadcast.sh /home/start_broadcast.sh
RUN chmod +x /home/start_broadcast.sh
ADD challenge.ts /home/dvb/bin/challenge.ts
ENTRYPOINT /home/start_broadcast.sh
