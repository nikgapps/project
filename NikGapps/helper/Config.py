import os

# The android version that we're targeting this application to run
TARGET_ANDROID_VERSION = 14

# Release type defines the release
# Possible values are [ 'canary', 'stable' ]
RELEASE_TYPE = "stable"
release_type = os.environ.get('RELEASE_TYPE')
if release_type is not None:
    RELEASE_TYPE = release_type

# Environment type differentiates the experimental and stable features
# Possible values are [ 'production', 'development' ]
ENVIRONMENT_TYPE = "production"
environment_type = os.environ.get('ENVIRONMENT_TYPE')
if environment_type is not None:
    ENVIRONMENT_TYPE = environment_type

# Possible Values are ['go', 'core', 'basic', 'omni', 'stock', 'full', 'addons', 'addonsets']
BUILD_PACKAGE_LIST = ['go', 'core', 'basic', 'omni', 'stock', 'full', 'addons', 'addonsets']

# Send the zip to device after creation, Possible values are True and False
SEND_ZIP_DEVICE = False
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

