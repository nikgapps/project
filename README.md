![](https://raw.githubusercontent.com/nikgapps/nikgapps.github.io/master/images/nikgapps-logo.webp)

# Introduction

NikGapps provides custom GApps packages tailored to individual needs, offering full configurability to install exactly the set of Google apps you want. Available in six variants, NikGapps is a unique GApps solution built from scratch to meet the needs of Android users.

## Features

- **Android Go Support**: Ideal for low-end devices, ensuring smooth performance.
- **Custom Architecture**: Installs GApps in `/product` and `/system_ext` partitions, with fallback to `/system` if space is limited.
- **Full Control**: Use `nikgapps.config` for installation preferences and `debloater.config` to remove unwanted components.
- **Compatibility**: Dirty flash support, and can be installed over ROMs with GApps (excluding Pixel-flavored ROMs).
- **Addons**: Includes useful addon packages, so you don't have to flash the entire GApps package for a single app.
- **Addon.d Support**: Custom addon.d script allows selective backup and restore of apps during dirty flashes.
- **Battery Optimization**: Optimize Google Play Services by turning off "Find My Device" (requires ROM support).
- **Privileged Permissions**: Ensures privileged apps get necessary permissions without disabling Privileged Permission Whitelisting.

## Build NikGapps Yourself

### Prerequisites

Ensure you have the following tools installed:

- **Linux/MacOS**: `sudo apt-get install -y --no-install-recommends python3 python3-pip aapt git git-lfs apktool`
- **Windows**: [Python3](https://www.python.org/), [Git](https://git-scm.com/), and [AAPT](https://packages.debian.org/buster/aapt).

### Steps

1. **Configure git user name and email to make Git LFS to work**
   ```bash
   git config --global user.name "Example"
   git config --global user.email "example@example.com"

2. **Set Up the Environment**:
   ```bash
   mkdir nikgapps
   cd nikgapps

3. **Create a virtual environment**

   Use ```python``` on Linux/MacOS and ```python3``` on Windows (you can figure out which command works for you by running ```python --version``` or ```python3 --version``` in cmd line)
   
   - On Linux/MacOS:  
      ```bash  
      python3 -m venv myvenv
      source myvenv\Scripts\activate
      
   - On Windows:
     ```bash  
     python -m venv myvenv
     myvenv\Scripts\activate

5. **Install builder from pip** 
   ```bash
   python3 -m pip install NikGapps
   
6. **You can now build given gapps variant**
   
   ```nikgapps --androidVersion (Android Version) --packageList (gapps variant)```
   
   *Example:*
   ```bash
   nikgapps --androidVersion 13 --packageList basic

**Your gapps package will be in Releases directory above nikgapps directory**

## Total Downloads  
<!-- 7312415 from 2019-07-22 to 2024-07-18 -->
<!-- 7653966 from 2019-07-22 to 2024-10-02 -->
![Static Badge](https://img.shields.io/badge/7.7M-red?label=Before%202nd%20Oct%202024&color=green)  
<img alt="SourceForge" src="https://img.shields.io/sourceforge/dt/nikgapps?label=After%202nd%20Oct%202024&color=red">   
<img alt="SourceForge" src="https://img.shields.io/sourceforge/dd/nikgapps?label=Downloads%20Per%20Day&color=blue">

<!--
sudo apt install binfmt-support qemu qemu-user-static

to run arm executable on arm64 devices
>
