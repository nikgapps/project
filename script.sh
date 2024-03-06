#!/bin/bash

# Exit on first error
set -e

# Setup SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Load SSH keys into ssh-agent
eval "$(ssh-agent -s)"

# Add SSH keys to the ssh-agent and configure known_hosts
{
    # Add SSH keys to the ssh-agent using environment variables
    echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -

    # Configure known_hosts to avoid prompts when connecting
    ssh-keyscan -H sourceforge.net
    ssh-keyscan -H github.com
    ssh-keyscan -H gitlab.com
} >> ~/.ssh/known_hosts

# Secure the known_hosts file
chmod 600 ~/.ssh/known_hosts

echo "SSH setup complete."

# Configure git with the provided username and email from environment variables
git config --global http.postBuffer 157286400
git config --global user.name "$USER_NAME"
git config --global user.email "$USER_EMAIL"

echo "Starting build process..."

# Using the environment variables directly in the nikgapps command
if [ "$UPDATE_WEBSITE" = "1" ]; then
    # Update the website in addition to the main command if required
    echo "Updating website..."
    nikgapps --sign --upload --release --androidVersion "$ANDROID_VERSION" --packageList "$PACKAGE_LIST" --updateWebsite
else
    # Proceed without updating the website
    nikgapps --sign --upload --release --androidVersion "$ANDROID_VERSION" --packageList "$PACKAGE_LIST"
fi

echo "Build process completed."
