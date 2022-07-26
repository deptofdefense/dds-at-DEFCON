#!/bin/bash
sudo apt-get update
sudo ./get-docker.sh
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y vlc wireshark okteta curl
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo usermod -aG docker $USER
newgrp docker << END
    docker image load --input docker-images.tar; docker-compose up
END