#!/bin/bash
USERNAME=ubuntu
GROUPNAME=ubuntu

if [ ! -z ${HOST_UID} ]; then

  if [ ! -z ${HOST_GID} ]; then
    HOST_GID=$HOST_UID
  fi

  echo "Adding group $GROUPNAME and username $USERNAME"

  groupadd -g $HOST_GID $GROUPNAME
  useradd --shell /bin/bash -u $HOST_UID -g $HOST_GID -o -c "" -m $USERNAME
  usermod -aG sudo $USERNAME

fi

# echo 'export PATH=$PATH:/usr/local/snap/bin' >> /home/$USERNAME/.bashrc
# echo 'export PATH=$PATH:/opt/miniconda/bin' >> /home/$USERNAME/.bashrc

/bin/bash "$@"
