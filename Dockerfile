FROM ubuntu:latest

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip aapt gcc python3-dev git git-lfs openjdk-8-jdk apktool dialog && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/nikgapps

# Install NikGapps from PyPI
RUN python3 -m pip install NikGapps

# Copy the script.sh into the container
COPY script.sh /usr/src/nikgapps

# Ensure script.sh is executable
RUN chmod +x /usr/src/nikgapps/script.sh

# Set script.sh as the entrypoint
ENTRYPOINT ["bash", "/usr/src/nikgapps/script.sh"]
