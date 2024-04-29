FROM ubuntu:latest

# Avoid prompts from apt during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv aapt gcc python3-dev git git-lfs openjdk-8-jdk apktool dialog openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/nikgapps

# Create a virtual environment and install Python packages
RUN python3 -m venv venv
ENV PATH="/usr/src/nikgapps/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install NikGapps

# Copy the script.sh into the container
COPY script.sh /usr/src/nikgapps

# Ensure script.sh is executable
RUN chmod +x /usr/src/nikgapps/script.sh

# Set script.sh as the entrypoint
ENTRYPOINT ["bash", "/usr/src/nikgapps/script.sh"]
