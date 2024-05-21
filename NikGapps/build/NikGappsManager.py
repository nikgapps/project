import json
import os

from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.Cmd import Cmd
from NikGapps.helper.Package import Package
from NikGapps.helper.Statics import Statics


class NikGappsManager:

    def __init__(self, android_version, arch="arm64"):
        self.android_version = android_version
        self.arch = arch
        self.source_directory = os.path.join(Statics.pwd,
                                             f"{android_version}_{arch}" if arch != "arm64" else f"{android_version}")

        self.packages = []
        self.appsets = []
        self.cmd = Cmd()
        self.package_data = {}
        # build_package_list, android_version, arch, sign_zip, send_zip_device, fresh_build, telegram, upload=None

        # we want to build a zip file for given package list, android version, arch
        # we also want to build a caching mechanism that doesn't rebuild the same package if it already exists
        # we are reading the directory to build package objects which can be used to copy the necessary files
        # we are copying the files because we don't want to copy over all the files.
        # we also need to have a list of all the packages to build the config file
        # we also need to have the ability to filter the package list based on the config file
        # so, we definitely need to have a config file object that reads from config file if it exists.
        # if the file doesn't exist, we need to load the defaults from package object that has all the packages loaded

    def initialize_packages(self, json_data):
        self.package_data = json_data

    def load_package_data(self, json_data):
        self.package_data = json_data
        return self.package_data

    def get_packages(self, package_type, android_version):
        match package_type:
            case 'core':
                return self.get_core_package(android_version)
            case 'basic':
                return self.get_basic_package(android_version)
            case 'omni':
                return self.get_omni_package(android_version)
            case 'stock':
                return self.get_stock_package(android_version)
            case 'full':
                return self.get_full_package(android_version)
            case 'go':
                return self.get_go_package()
            case 'all':
                return self.get_all_packages(android_version)
            case 'addon':
                return self.get_addon_packages(android_version)
            case _:
                return self.get_package_by_name_or_title(package_type)

    def get_package_by_name_or_title(self, package_type):
        try:
            # Attempt to fetch by package name
            package = self.create_package(package_type)
            return [self.get_app_set(package)]
        except ValueError:
            # Attempt to fetch by package title
            for app_set in self.get_full_package(self.android_version):
                if str(app_set.title).lower() == str(package_type).lower():
                    return [app_set]
                for package in app_set.package_list:
                    if str(package.package_title).lower() == str(package_type).lower():
                        return [AppSet(app_set.title, [package])]
            for app_set in self.get_go_package():
                if str(app_set.title).lower() == str(package_type).lower():
                    return [app_set]
                for package in app_set.package_list:
                    if str(package.package_title).lower() == str(package_type).lower():
                        return [AppSet(app_set.title, [package])]
            return [None]

    def get_package_details(self, package_name):
        if package_name in self.package_data:
            return self.package_data[package_name]
        else:
            raise ValueError(f"No details found for package: {package_name}")

    def get_app_set(self, pkg: Package, title=None):
        if title is None:
            name = pkg.package_title
        else:
            name = title
        return AppSet(name, [pkg])

    def create_package(self, package_name):
        package_details = self.get_package_details(package_name)
        # Assume we pick the first entry if there are multiple entries
        package_info = package_details[0]
        return Package(
            title=package_info['title'],
            package_name=package_name,
            app_type=Statics.is_priv_app if package_info['type'] == "priv-app" else Statics.is_system_app,
            package_title=package_info['title']
        )

    def get_go_package(self):
        app_set_list = []

        core_go = AppSet("CoreGo")
        packages_to_add = [
            "com.google.android.gms",
            "com.android.vending",
            "com.google.android.gsf",
            "com.google.android.syncadapters.contacts",
            "com.google.android.syncadapters.calendar"
        ]

        for package_name in packages_to_add:
            package = self.create_package(package_name)
            core_go.add_package(package)
        app_set_list.append(core_go)

        go_packages = [
            "com.google.android.apps.searchlite",
            "com.google.android.apps.assistant",
            "com.google.android.apps.mapslite",
            "com.google.android.apps.navlite",
            "com.google.android.apps.photosgo",
            "com.google.android.gm.lite"
        ]

        for package_name in go_packages:
            package = self.create_package(package_name)
            app_set_list.append(AppSet(package.package_title, [package]))

        return app_set_list

    def get_core_package(self, android_version):
        app_set_list = []

        core = AppSet("Core")
        core_packages = [
            "com.google.android.gms",
            "com.android.vending",
            "com.google.android.gsf",
            "com.google.android.syncadapters.contacts",
            "com.google.android.syncadapters.calendar"
        ]

        for package_name in core_packages:
            package = self.create_package(package_name)
            core.add_package(package)
        app_set_list.append(core)

        return app_set_list

    def get_basic_package(self, android_version):
        app_set_list = self.get_core_package(android_version)

        basic_packages = [
            "com.google.android.apps.wellbeing",
            "com.google.android.apps.messaging",
            "com.google.android.dialer",
            "com.google.android.contacts",
            "com.google.android.ims"
        ]

        for package_name in basic_packages:
            package = self.create_package(package_name)
            app_set_list.append(AppSet(package.package_title, [package]))

        app_set_list.append(self.get_google_clock(android_version))
        return app_set_list

    def get_omni_package(self, android_version):
        app_set_list = self.get_basic_package(android_version)

        omni_packages = [
            "com.google.android.setupwizard",
            "com.google.android.calculator",
            "com.google.android.apps.docs",
            "com.google.android.apps.maps",
            "com.google.android.gms.location.history",
            "com.google.android.apps.photos",
            "com.google.android.apps.turbo",
            "com.google.android.inputmethod.latin",
            "com.google.android.calendar",
            "com.google.android.keep"
        ]

        for package_name in omni_packages:
            package = self.create_package(package_name)
            app_set_list.append(AppSet(package.package_title, [package]))

        return app_set_list

    def get_stock_package(self, android_version):
        app_set_list = self.get_omni_package(android_version)

        stock_packages = [
            "com.google.android.play.games",
            "com.google.android.apps.nexuslauncher",
            "com.google.android.apps.recorder",
            "com.google.android.apps.nbu.files",
            "com.google.android.markup",
            "com.google.android.tts",
            "com.google.android.googlequicksearchbox",
            "com.google.android.soundpicker"
        ]

        for package_name in stock_packages:
            package = self.create_package(package_name)
            app_set_list.append(AppSet(package.package_title, [package]))

        return app_set_list

    def get_full_package(self, android_version):
        app_set_list = self.get_stock_package(android_version)

        full_packages = [
            "com.android.chrome",
            "com.google.android.gm",
            "com.google.android.apps.work.oobconfig",
            "com.google.android.projection.gearhead",
            "com.google.android.feedback",
            "com.google.android.partnersetup",
            "com.google.android.apps.work.clouddpc"
        ]

        for package_name in full_packages:
            package = self.create_package(package_name)
            app_set_list.append(AppSet(package.package_title, [package]))

        return app_set_list

    def get_addon_packages(self, android_version):
        addon_set_list = []

        addon_packages = [
            "com.google.android.apps.tycho",
            "com.google.android.apps.tachyon",
            "com.google.android.apps.docs.editors.docs",
            "com.google.android.apps.docs.editors.sheets",
            "com.google.android.apps.docs.editors.slides",
            "com.google.android.youtube",
            "com.google.android.apps.youtube.music",
            "com.google.android.apps.books",
            "com.google.android.marvin.talkback",
            "com.google.android.apps.wallpaper.pixel"
        ]

        for package_name in addon_packages:
            package = self.create_package(package_name)
            addon_set_list.append(AppSet(package.package_title, [package]))

        return addon_set_list

    def get_all_packages(self, android_version):
        all_package_list = []
        for app_set in self.get_full_package(android_version):
            all_package_list.append(app_set)
        for app_set in self.get_go_package():
            all_package_list.append(app_set)
        for app_set in self.get_addon_packages(android_version):
            all_package_list.append(app_set)
        return all_package_list

    def get_addonsets(self, android_version):
        addon_set_list = []
        for app_set in self.get_full_package(android_version):
            if app_set.title in ['Core', 'Pixelize']:
                continue
            addon_set_list.append(app_set)
        for app_set in self.get_go_package():
            if app_set.title in ['CoreGo']:
                continue
            addon_set_list.append(app_set)
        return addon_set_list