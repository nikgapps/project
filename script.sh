#!/bin/bash

# Exit on first error
set -e

# Enable debugging to print each command before it's executed
# set -x
# Disabling logging since the script is working fine now, can be re-enabled later for debugging purposes

# Setup SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh
which ssh-keyscan || (apt-get update && apt-get install -y openssh-client)
# Start ssh-agent
eval "$(ssh-agent -s)"

# Add SSH private key to the ssh-agent
echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -

# Add SSH keys to known_hosts to avoid prompts
ssh-keyscan -H frs.sourceforge.net >> ~/.ssh/known_hosts || echo "Failed to scan frs.sourceforge.net"
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

[[ "$SIGN" == "1" ]] && nikgapps_cmd+=" --sign"
[[ "$UPLOAD" == "1" ]] && nikgapps_cmd+=" --upload"
[[ "$RELEASE" == "1" ]] && nikgapps_cmd+=" --release"
nikgapps_cmd+=" --androidVersion \"$ANDROID_VERSION\" --packageList \"$PACKAGE_LIST\""
[[ "$UPDATE_WEBSITE" == "1" ]] && nikgapps_cmd+=" --updateWebsite"

echo "Executing command: $nikgapps_cmd"
eval "$nikgapps_cmd"

echo "Build process completed."
