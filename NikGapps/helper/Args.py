import argparse
# from helper.B64 import B64


class Args:
    def __init__(self, parser=None) -> None:
        if parser is None:
            self.parser = argparse.ArgumentParser(
                description="NikGapps build command help!")
        # parser.add_argument(
        #     '-U', '--userID', help="Telegram User Id", default='-1', type=str)
        self.parser.add_argument('-C', '--config', help="byte64 value of nikgapps.config", type=str)
        # parser.add_argument(
        #     '-N', '--configName', help="Name of custom nikgapps.config", type=str)
        # parser.add_argument(
        #     '-O', '--oems', help="It is the OEM from which we need to fetch the gapps", default="-1", type=str)
        self.parser.add_argument('-c', '--cache', help="Use this to operate on cached apks", action="store_true")
        self.parser.add_argument('-a', '--arch', help="It is the architecture for which we need to build the gapps",
                                 default="arm64", type=str)
        self.parser.add_argument('-T', '--tar', help="Use this to make highly compressed builds", action="store_true")
        self.parser.add_argument(
            '-G', '--disableGitClone', help="Include this to disable git clone operation", action="store_true")
        self.parser.add_argument(
            '-W', '--updateWebsite', help="Include this to update nikgapps website with changelog", action="store_true")
        self.parser.add_argument('-U', '--upload', help="Use this to enable Upload Functionality", action="store_true")
        self.parser.add_argument('-X', '--sign', help="Use this to sign the zip", action="store_true")
        self.parser.add_argument('-R', '--release', help="Use this to mark the Release", action="store_true")
        # parser.add_argument(
        #     '-F', '--skipForceRun', help="Overrides the release constraints and doesn't run the program",
        #     action="store_true")
        self.parser.add_argument(
            '-A', '--androidVersion', help="It is the android version for which we need to build the gapps",
            default="-1", type=str)
        self.parser.add_argument('-P', '--packageList', help="List of packages to build", type=str)

        args = self.parser.parse_args()

        self.arch = args.arch
        # self.user_id = args.userID
        self.config_value = args.config
        self.upload = args.upload
        self.sign = args.sign
        self.tar = args.tar
        self.release = args.release
        # self.enable_git_check = args.enableGitCheck
        self.enable_git_clone = not args.disableGitClone
        self.android_version = args.androidVersion
        self.package_list = args.packageList
        # self.forceRun = args.forceRun
        # self.config_name = args.configName
        self.update_website = args.updateWebsite
        self.use_cached_apks = args.cache
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
