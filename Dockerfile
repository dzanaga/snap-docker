FROM ubuntu

RUN apt-get update && \
    apt-get install -y wget sudo && \
    wget http://step.esa.int/downloads/6.0/installers/esa-snap_sentinel_unix_6_0.sh && \
    bash esa-snap_sentinel_unix_6_0.sh -q

RUN echo "%sudo  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    apt-get install -y gosu; \
	  rm -rf /var/lib/apt/lists/*; 

ADD entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT /bin/bash /usr/local/bin/entrypoint.sh
