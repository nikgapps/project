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

### Local development defaults

Configure defaults in `NikGapps/helper/Config.py`. The current target is Android
17, Core, ARM64. `BUILD_PACKAGE_LIST` lists supported variants;
`DEFAULT_PACKAGE_LIST` selects the default variants.

`RELEASE_TYPE` selects the release/channel: `stable`, `beta`, or `canary`.
`ENVIRONMENT_TYPE` selects where packages come from by default:

| Environment | Release type | Default source | Package selection |
|---|---|---|---|
| `local`, `dev`, `development` | `stable` | `local` | `17_stable` |
| `local`, `dev`, `development` | `beta` | `local` | `17_beta` |
| `production`, `release` | `stable` | `registry` | Android 17 stable catalog |
| `production`, `release` | `beta` | `registry` | Android 17 beta catalog, if published |

`development` is an alias for `dev`; `release` is an alias for `production`.
`PACKAGE_SOURCE` may explicitly override the default with `local`, `git`, or
`registry`. `PACKAGE_CHANNEL` normally follows `RELEASE_TYPE`; an explicit
registry channel override is allowed. Git/local builds reject a channel that
conflicts with release type. Command-line arguments override their configured
defaults. Environment variables also override defaults and are loaded from `.env`.

Run from `D:\workspace\python\project`. Clear optional overrides first if switching
back to automatic selection:

```powershell
Set-Location D:\workspace\python\project
Remove-Item Env:PACKAGE_SOURCE,Env:PACKAGE_CHANNEL -ErrorAction SilentlyContinue
# Also remove these overrides from .env if present.
```

Local stable build, using `17_stable` and `overlays_17` without cloning:

```powershell
$env:ENVIRONMENT_TYPE = 'local'
$env:RELEASE_TYPE = 'stable'
.\.venv\Scripts\python.exe -m NikGapps.main
```

Local beta build, using `17_beta` and the same `overlays_17`:

```powershell
$env:ENVIRONMENT_TYPE = 'local'
$env:RELEASE_TYPE = 'beta'
.\.venv\Scripts\python.exe -m NikGapps.main
# Or use --releaseType beta instead of setting RELEASE_TYPE.
```

Registry build from the published stable packages:

```powershell
$env:ENVIRONMENT_TYPE = 'production'
$env:RELEASE_TYPE = 'stable'
.\.venv\Scripts\python.exe -m NikGapps.main
```

Production retains the established release-tracker behavior; uploading is still
opt-in via `--upload`. To test registry packages locally without production
release marking:

```powershell
$env:ENVIRONMENT_TYPE = 'local'
$env:RELEASE_TYPE = 'stable'
.\.venv\Scripts\python.exe -m NikGapps.main --packageSource registry
```

To clone/update the source repositories instead of using existing directories:

```powershell
.\.venv\Scripts\python.exe -m NikGapps.main --packageSource git --releaseType beta
```

Local mode discovers `<Android version>_<release type>` and `overlays_<version>`
beside the project directory. `APK_SOURCE` and `OVERLAY_SOURCE`, in Config.py or
the environment, override those paths. Local mode does not clone or mark a Git
release. Changing to `--androidVersion 16` selects the equivalent Android 16
sources/catalog. Outputs go to `D:\workspace\python\Releases\<version>`.

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
      source myvenv/bin/activate
      
   - On Windows:
     ```bash  
     python -m venv myvenv
     myvenv\bin\activate

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
