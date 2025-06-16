#!/bin/bash

# Install Docker Compose plugin if missing
mkdir -p ~/.docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 \
  -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

# Clone repo if it doesn't exist
cd ~
if [ ! -d "states-api" ]; then
  git clone https://github.com/YOUR_USERNAME/states-api.git
fi

# Ensure we're on main and up-to-date
cd ~/states-api
git checkout main
git pull origin main

