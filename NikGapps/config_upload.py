from NikGapps.config.NikGappsConfig import NikGappsConfig
from NikGapps.helper.Args import Args
from NikGapps.helper import Config


def config_upload():
    args = Args()
    android_versions = [Config.TARGET_ANDROID_VERSION]
    if len(args.get_android_versions()) > 0:
        android_versions = args.get_android_versions()

    for android_version in android_versions:
        if args.upload:
            Config.UPLOAD_FILES = True
            print("Uploading NikGapps Config for " + android_version)
            config = NikGappsConfig(android_version)
            config.upload_nikgapps_config()


if __name__ == "__main__":
    config_upload()
