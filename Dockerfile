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

# set gpt max memory to 4GB
# RUN sed -i -e 's/-Xmx1G/-Xmx4G/g' /usr/local/snap/bin/gpt.vmoptions

# COPY graph_template.xml /tmp/template/
# COPY snap_internal.py /tmp/scripts/snap_internal.py
# COPY entrypoint.sh /tmp/scripts/entrypoint.sh
#
# RUN chmod +x /tmp/scripts/entrypoint.sh
#
# ENTRYPOINT /tmp/scripts/entrypoint.sh
