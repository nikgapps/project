#!/bin/bash

# Exit on first error
set -e

# Enable debugging to print each command before it's executed
set -x

# Setup SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh
which ssh-keyscan || (apt-get update && apt-get install -y openssh-client)
# Start ssh-agent
eval "$(ssh-agent -s)"

# Add SSH private key to the ssh-agent
echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -

# Add SSH keys to known_hosts to avoid prompts
ssh-keyscan -H sourceforge.net >> ~/.ssh/known_hosts || echo "Failed to scan sourceforge.net"
ssh-keyscan -H github.com >> ~/.ssh/known_hosts || echo "Failed to scan github.com"
ssh-keyscan -H gitlab.com >> ~/.ssh/known_hosts || echo "Failed to scan gitlab.com"

# Secure the known_hosts file
chmod 600 ~/.ssh/known_hosts

echo "SSH setup complete."

# Configure git with the provided username and email from environment variables
git config --global http.postBuffer 157286400
git config --global user.name "$USER_NAME"
git config --global user.email "$USER_EMAIL"

echo "Starting build process..."

# Construct nikgapps command dynamically
nikgapps_cmd="nikgapps"
if [ "$SIGN" = "1" ]; then
    nikgapps_cmd+=" --sign"
fi
if [ "$UPLOAD" = "1" ]; then
    nikgapps_cmd+=" --upload"
fi
if [ "$RELEASE" = "1" ]; then
    nikgapps_cmd+=" --release"
fi
nikgapps_cmd+=" --androidVersion \"$ANDROID_VERSION\" --packageList \"$PACKAGE_LIST\""
if [ "$UPDATE_WEBSITE" = "1" ]; then
    nikgapps_cmd+=" --updateWebsite"
fi

echo "Executing: $nikgapps_cmd"
eval "$nikgapps_cmd"

echo "Build process completed."
