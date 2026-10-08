import os
from dotenv import load_dotenv

load_dotenv()

# The android version that we're targeting this application to run
TARGET_ANDROID_VERSION = 17
PACKAGE_ARCH = os.environ.get('PACKAGE_ARCH', 'arm64')
DEFAULT_PACKAGE_LIST = ['core']

# Release type defines the release
# Selects the package channel and source repository suffix: stable/beta/canary.
RELEASE_TYPE = os.environ.get('RELEASE_TYPE', 'stable').strip().lower()

# Environment type differentiates the experimental and stable features
# production/release uses the registry; dev/development/local uses local sources.
ENVIRONMENT_TYPE = os.environ.get('ENVIRONMENT_TYPE', 'dev').strip().lower()
ENVIRONMENT_TYPE = {'release': 'production', 'development': 'dev'}.get(ENVIRONMENT_TYPE, ENVIRONMENT_TYPE)

# Possible Values are ['go', 'core', 'basic', 'omni', 'stock', 'full', 'addons', 'addonsets']
BUILD_PACKAGE_LIST = ['go', 'core', 'basic', 'omni', 'stock', 'full', 'addons', 'addonsets']

# Send the zip to device after creation, Possible values are True and False
SEND_ZIP_DEVICE = True if ENVIRONMENT_TYPE == "dev" and RELEASE_TYPE in ("dev", "beta") else False
SEND_ZIP_LOCATION = "/sdcard"

# This will allow the program to sign the zip
SIGN_ZIP = False

# When Fresh Build is True, the installer.sh will freshly build the zip (Comparatively Slower)
# When Fresh Build is False, the installer.sh picks up existing zip and builds gapps package (Faster)
FRESH_BUILD = True

# DEBUG_MODE will be helpful in printing more stuff so program can be debugged
DEBUG_MODE = True
if ENVIRONMENT_TYPE.__eq__("production"):
    DEBUG_MODE = False

# True if we want the files to upload as soon as they get created
UPLOAD_FILES = False

# True if we want to use cached apks
USE_CACHED_APKS = False

# Override the execution if we re-trigger the workflow
OVERRIDE_RELEASE = True

# Git Check enables controlled releases.
# If this is set to True, new release will only happen when there is a change in the source repo or apk is updated
GIT_CLONE_SOURCE = True
GIT_CHECK = True
GIT_PUSH = True

# Overlays, Gapps Apks and Cached Apks source
CACHED_SOURCE = None
APK_SOURCE = os.environ.get('APK_SOURCE')
OVERLAY_SOURCE = os.environ.get('OVERLAY_SOURCE')

# "registry": published catalog; "git": clone source repositories;
# "local": existing VERSION_stable and overlays_VERSION directories beside project.
PACKAGE_SOURCE = os.environ.get("PACKAGE_SOURCE", "registry" if ENVIRONMENT_TYPE == "production" else "local").strip().lower()
PACKAGE_CHANNEL = os.environ.get("PACKAGE_CHANNEL", RELEASE_TYPE).strip().lower()


def default_package_channel(release_type):
    # Explicit environment/config overrides win; otherwise follow the effective
    # release type, including a --releaseType argument.
    if 'PACKAGE_CHANNEL' in os.environ or PACKAGE_CHANNEL != RELEASE_TYPE:
        return PACKAGE_CHANNEL
    return release_type


def local_source_paths(android_version, source_root):
    source = APK_SOURCE or os.path.join(source_root, f"{android_version}_{RELEASE_TYPE}")
    overlays = OVERLAY_SOURCE or os.path.join(source_root, f"overlays_{android_version}")
    if not os.path.isdir(source):
        raise ValueError(f"Local APK source does not exist: {source}")
    if float(android_version) >= 12.1 and not os.path.isdir(overlays):
        raise ValueError(f"Local overlay source does not exist: {overlays}")
    return str(source), str(overlays)
PACKAGE_CATALOG_URL = os.environ.get(
    "PACKAGE_CATALOG_URL",
    "https://gitlab.com/nikgapps/nikgapps-package-catalog/-/raw/main/catalog.json"
)
PACKAGE_APPSETS_URL = os.environ.get(
    "PACKAGE_APPSETS_URL",
    "https://gitlab.com/nikgapps/nikgapps-package-catalog/-/raw/main/appsets.json"
)
PACKAGE_RELEASE_INDEX_URL = os.environ.get(
    "PACKAGE_RELEASE_INDEX_URL",
    "https://gitlab.com/nikgapps/nikgapps-package-catalog/-/raw/main/releases/index.json"
)
PACKAGE_RELEASE_ID = os.environ.get("PACKAGE_RELEASE_ID")
PACKAGE_CACHE = os.environ.get(
    "PACKAGE_CACHE",
    os.path.abspath(os.path.join(os.getcwd(), ".nikgapps-package-cache"))
)
PACKAGE_CHANNEL_OVERRIDES = os.environ.get("PACKAGE_CHANNEL_OVERRIDES", "{}")

# Enabling this will enable the feature of building NikGapps using config file
BUILD_CONFIG = True
BUILD_EXCLUSIVE = (RELEASE_TYPE.lower().__eq__("stable"))
EXCLUSIVE_FOLDER = "Elite"

PROJECT_MODE = "build"

# This will help fetch the files which requires root access such as overlay files
ADB_ROOT_ENABLED = False

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
NIKGAPPS_CHAT_ID = os.environ.get('NIKGAPPS_CHAT_ID')
MESSAGE_THREAD_ID = os.environ.get('MESSAGE_THREAD_ID')
ELITE_MESSAGE_THREAD_ID = os.environ.get('ELITE_MESSAGE_THREAD_ID')

