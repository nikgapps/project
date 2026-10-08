import argparse
from NikGapps.helper import Config


# from helper.B64 import B64


class Args:
    def __init__(self, parser=None) -> None:
        self.parser = parser or argparse.ArgumentParser(
            description="NikGapps build command help!",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        # parser.add_argument(
        #     '-U', '--userID', help="Telegram User Id", default='-1', type=str)
        self.parser.add_argument('-C', '--configValue', help="byte64 value of nikgapps.config", type=str)
        self.parser.add_argument(
            '-N', '--configName', help="Name of custom nikgapps.config", type=str)
        # parser.add_argument(
        #     '-O', '--oems', help="It is the OEM from which we need to fetch the gapps", default="-1", type=str)
        self.parser.add_argument('-c', '--cache', help="Use this to operate on cached apks", action="store_true")
        self.parser.add_argument('-a', '--arch', help="It is the architecture for which we need to build the gapps",
                                 default=Config.PACKAGE_ARCH, type=str)
        self.parser.add_argument('-T', '--tar', help="Use this to make highly compressed builds", action="store_true")
        self.parser.add_argument(
            '-G', '--disableGitClone', help="Include this to disable git clone operation",
            default=not Config.GIT_CLONE_SOURCE, action="store_true")
        self.parser.add_argument(
            '-W', '--updateWebsite', help="Include this to update nikgapps website with changelog", action="store_true")
        self.parser.add_argument('-U', '--upload', help="Use this to enable Upload Functionality", action="store_true")
        self.parser.add_argument('-X', '--sign', help="Use this to sign the zip", action="store_true")
        self.parser.add_argument('-R', '--release', help="Use this to mark the Release", action="store_true")
        self.parser.add_argument('-S', '--sshClone', help="Use this to clone with SSH", action="store_true")
        self.parser.add_argument('-D', '--sendToDevice', help="Use this to enable sending zip to connected device", action="store_true")
        # parser.add_argument(
        #     '-F', '--skipForceRun', help="Overrides the release constraints and doesn't run the program",
        #     action="store_true")
        self.parser.add_argument(
            '-A', '--androidVersion', help="It is the android version for which we need to build the gapps",
            default=str(Config.TARGET_ANDROID_VERSION), type=str)
        self.parser.add_argument(
            '-r', '--releaseType', help="It is the release type for which we need to build the gapps",
            default=Config.RELEASE_TYPE, type=str)
        self.parser.add_argument('-P', '--packageList', help="List of packages to build",
                                 default=','.join(Config.DEFAULT_PACKAGE_LIST), type=str)
        self.parser.add_argument(
            '--packageSource', choices=['git', 'registry', 'local'], default=Config.PACKAGE_SOURCE,
            help="Use cloned Git sources, the package registry, or existing local source directories"
        )
        self.parser.add_argument(
            '--packageChannel', choices=['stable', 'beta', 'canary'],
            help="Channel override; otherwise follows RELEASE_TYPE"
        )

        args = self.parser.parse_args()

        self.arch = args.arch
        # self.user_id = args.userID
        self.config_value = args.configValue
        self.upload = args.upload
        self.sign = args.sign
        self.tar = args.tar
        self.release = args.release
        # self.enable_git_check = args.enableGitCheck
        self.enable_git_clone = not args.disableGitClone
        self.android_version = args.androidVersion
        self.package_list = args.packageList
        # self.forceRun = args.forceRun
        self.config_name = args.configName
        self.update_website = args.updateWebsite
        self.use_cached_apks = args.cache
        self.release_type = args.releaseType
        self.ssh_clone = args.sshClone
        self.send_zip_device = args.sendToDevice
        self.package_source = args.packageSource
        self.package_channel = args.packageChannel or Config.default_package_channel(args.releaseType)
        if self.package_source != 'registry' and self.package_channel != self.release_type:
            self.parser.error("Git/local sources follow releaseType; use --releaseType to select stable/beta/canary")
        # self.oems = args.oems

    def get_package_list(self):
        if self.config_value is None and self.package_list is not None:
            pkg_list = str(self.package_list).replace("'", "").split(',')
        elif self.config_value is not None:
            # generate from config
            # config_string = B64.b64d(self.config_value)
            pkg_list = str(self.package_list).replace("'", "").split(',')
        else:
            pkg_list = []
        return pkg_list

    # def get_oems(self):
    #     if self.oems != str(-1):
    #         oems = self.oems.split(',')
    #     else:
    #         oems = []
    #     return oems

    def get_android_versions(self):
        if self.android_version != str(-1):
            android_versions = str(self.android_version).replace("'", "").split(',')
        else:
            android_versions = []
        return android_versions
