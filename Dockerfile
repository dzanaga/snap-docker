FROM ubuntu

RUN apt-get update; \
    apt-get install -y wget sudo gosu; \
    wget http://step.esa.int/downloads/6.0/installers/esa-snap_sentinel_unix_6_0.sh; \
    bash esa-snap_sentinel_unix_6_0.sh -q; \
    rm esa-snap_sentinel_unix_6_0.sh; \
    echo "%sudo  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers; \
    apt-get install -y gosu; \
	  rm -rf /var/lib/apt/lists/*; \
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda.sh; \
    bash /opt/miniconda.sh -b -p /opt/miniconda; \
    rm /opt/miniconda.sh; \
    chgrp -R sudo /opt/miniconda; \
    chmod 777 -R /opt/miniconda

COPY S1_GraphTemplate.xml /tmp/template/S1_GraphTemplate.xml
COPY snap_internal.py /tmp/scripts/snap_internal.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh


# COPY inner_snap.py /usr/local/bin/inner_snap.py

# ENTRYPOINT /usr/local/bin/entrypoint.sh
# CMD /bin/bash /usr/local/bin/entrypoint.sh
