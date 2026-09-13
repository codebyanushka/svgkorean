#!/bin/bash
# Run this ONCE on a fresh AWS EC2 Ubuntu instance (e.g. t3.micro) after
# connecting to it. Installs Docker + Compose plugin and adds a swap file
# (t3.micro only has 1GB RAM - Postgres + backend + nginx together need the
# extra headroom to avoid the OOM killer under memory spikes).
# Usage: bash deploy/aws-setup.sh
set -euo pipefail

echo "Updating packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo "Installing Docker..."
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"

echo "Adding a 2GB swap file (t3.micro only has 1GB RAM)..."
if [ ! -f /swapfile ]; then
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi
free -h

echo "Done. Log out and back in for the docker group change to take effect."
echo "Also make sure your EC2 Security Group has inbound rules for TCP 80 and"
echo "443 (source 0.0.0.0/0) - port 22 alone (already open) isn't enough for"
echo "the app to be reachable from the internet."
