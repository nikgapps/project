#!/bin/bash

# Assign arguments to variables
GIT_USER_NAME=$1
GIT_USER_EMAIL=$2
ANDROID_VERSION=$3
PACKAGE_LIST=$4

# Configure git with the provided username and email
git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"

echo "nikgapps -A $ANDROID_VERSION -P $PACKAGE_LIST"
# Now run nikgapps with the provided Android version and package list
nikgapps -A $ANDROID_VERSION -P $PACKAGE_LIST
