import os

from NikGapps.build.PackageConstants import PackageConstants
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.Cmd import Cmd
from NikGapps.helper.Package import Package
from NikGapps.helper.Statics import Statics
from NikGapps.helper.overlay.Overlay import Overlay
from NikGapps.helper.overlay.Library import Library


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
        self.extra_files_exceptions = {
            "extra.files": "ExtraFiles",
            "extra.files.go": "ExtraFilesGo"
        }

    def initialize_packages(self, json_data):
        self.package_data = json_data

    def get_packages(self, package_type):
        match package_type:
            case 'core':
                return self.get_core_package()
            case 'basic':
                return self.get_basic_package()
            case 'omni':
                return self.get_omni_package()
            case 'stock':
                return self.get_stock_package()
            case 'full':
                return self.get_full_package()
            case 'go':
                return self.get_go_package()
            case 'all':
                return self.get_all_packages()
            case _:
                return self.get_package_by_name_or_title(package_type)

    def get_package_by_name_or_title(self, package_type):
        if str(package_type).lower() == "addons":
            return self.get_addon_packages()
        if str(package_type).lower() == "addonsets":
            return self.get_addonsets()
        else:
            for app_set in self.get_addon_packages():
                if str(app_set.title).lower() == str(package_type).lower():
                    return [app_set]
                for package in app_set.package_list:
                    if str(package.package_title).lower() == str(package_type).lower():
                        return [AppSet(app_set.title, [package])]
            for app_set in self.get_full_package():
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

    def get_app_set_title(self, package_name, look_into_match=None):
        package_details = self.package_data.get(package_name, {})
        if package_details:
            appset_list = package_details[0]['appset']
            for appset in appset_list:
                if look_into_match:
                    if str(appset).__contains__(look_into_match):
                        return str(appset)
                else:
                    return str(appset)
        return None

    def create_appset_list(self, package_list, look_into_match=False):
        appset_dict = {}
        for package in package_list:
            appset_title = self.get_app_set_title(package.package_name, look_into_match)
            if appset_title not in appset_dict:
                appset_dict[appset_title] = AppSet(appset_title, [package])
            else:
                appset_dict[appset_title].package_list.append(package)
        return list(appset_dict.values())

    def create_appset_list_from_packages(self, package_list, look_into_match=None):
        appset_dict = {}
        for package_name in package_list:
            package = self.create_package(package_name)
            appset_title = self.get_app_set_title(package_name, look_into_match)
            if appset_title not in appset_dict:
                appset_dict[appset_title] = AppSet(appset_title, [package])
            else:
                appset_dict[appset_title].package_list.append(package)
        return list(appset_dict.values())

    def create_package(self, package_name):
        if package_name in self.extra_files_exceptions:
            package = Package(
                title=self.extra_files_exceptions[package_name],
                package_name=package_name,
            )
        else:
            package_details = self.get_package_details(package_name)
            package_info = package_details[0]
            package = Package(
                title=package_info['title'],
                package_name=package_name,
                app_type=Statics.is_priv_app if package_info['type'] == "priv-app" else Statics.is_system_app,
                package_title=package_info['package_title'],
                partition=package_info['partition'] if float(self.android_version) > 10 else "product"
            )
            if float(self.android_version) > 12:
                overlays = self.get_package_overlays(package_name)
                for overlay in overlays:
                    package.add_overlay(overlay)
            deletes = PackageConstants.get_package_deletes(package_name)
            for delete in deletes:
                package.delete(delete)
            package.clean_flash_only = PackageConstants.get_package_clean_flash_rule(package_name)
        script = PackageConstants.get_package_script(package_name)
        if script:
            package.additional_installer_script = script
        return package

    def get_package_overlays(self, package_name):
        if not float(self.android_version) > 12:
            return []
        package_overlays = {
            "com.google.android.gms": [
                {
                    "package_name": "com.nikgapps.overlay.gmscore",
                    "resources": Library.get_gms_core_resources()
                }
            ],
            "com.google.android.dialer": [
                {
                    "package_name": "com.nikgapps.overlay.dialer",
                    "resources": Library.get_google_dialer_resources()
                }
            ],
            "com.google.android.contacts": [
                {
                    "package_name": "com.nikgapps.overlay.contacts",
                    "resources": Library.get_google_contacts_resources()
                }
            ],
            "com.google.android.tts": [
                {
                    "package_name": "com.nikgapps.overlay.googletts",
                    "resources": Library.get_google_tts_resources()
                }
            ],
            "com.google.android.apps.wellbeing": [
                {
                    "package_name": "com.nikgapps.overlay.wellbeing",
                    "resources": Library.get_digital_wellbeing_resources()
                }
            ],
            "com.google.android.marvin.talkback": [
                {
                    "package_name": "com.nikgapps.overlay.talkback",
                    "resources": Library.get_google_talkback_resources()
                }
            ],
            "com.google.android.flipendo": [
                {
                    "package_name": "com.nikgapps.overlay.flipendo",
                    "resources": Library.get_flipendo_resources()
                }
            ],
            "com.google.android.apps.messaging": [
                {
                    "package_name": "com.nikgapps.overlay.messages",
                    "resources": Library.get_google_messages_resources()
                }
            ],
            "com.google.android.gms.location.history": [
                {
                    "package_name": "com.nikgapps.overlay.googlelocationhistory",
                    "resources": Library.get_google_location_history_resources()
                }
            ],
            "com.google.android.apps.photos": [
                {
                    "package_name": "com.nikgapps.overlay.googlephotos",
                    "resources": Library.get_google_photos_resources()
                }
            ],
            "com.google.android.settings.intelligence": [
                {
                    "package_name": "com.nikgapps.overlay.settingsintelligence",
                    "resources": Library.get_settings_services_resources(self.android_version)
                }
            ],
            "com.google.android.projection.gearhead": [
                {
                    "package_name": "com.nikgapps.overlay.androidauto",
                    "resources": Library.get_android_auto_resources()
                }
            ],
            "com.google.android.apps.nexuslauncher": [
                {
                    "package_name": "com.nikgapps.overlay.pixellauncher",
                    "resources": Library.get_pixel_launcher_resources()
                }
            ],
            "com.google.android.googlequicksearchbox": [
                {
                    "package_name": "com.nikgapps.overlay.googlequicksearchbox",
                    "resources": Library.get_velvet_resources()
                }
            ],
            "com.google.android.deskclock": [
                {
                    "package_name": "com.nikgapps.overlay.googleclock",
                    "resources": Library.get_google_clock_resources()
                }
            ],
            "com.google.android.as": [
                {
                    "package_name": "com.nikgapps.overlay.ais",
                    "resources": Library.get_devices_personalization_services_resources()
                }
            ],
            "com.google.android.wallpaper.effects": [
                {
                    "package_name": "com.nikgapps.overlay.cinematiceffect",
                    "resources": Library.get_cinematic_effect_resources()
                }
            ],
            "com.google.android.apps.youtube.music": [
                {
                    "package_name": "com.nikgapps.overlay.youtubemusic",
                    "resources": Library.get_youtube_music_resources()
                }
            ]
        }
        return [Overlay(package_name, overlay["package_name"], self.android_version, overlay["resources"]) for overlay
                in package_overlays.get(package_name, [])]

    def get_go_package(self):
        go_packages = [
            "extra.files.go",
            "com.google.android.gms",
            "com.android.vending",
            "com.google.android.gsf",
            "com.google.android.syncadapters.contacts",
            "com.google.android.syncadapters.calendar",
            "com.google.android.apps.searchlite",
            "com.google.android.apps.assistant",
            "com.google.android.apps.mapslite",
            "com.google.android.apps.navlite",
            "com.google.android.apps.photosgo",
            "com.google.android.gm.lite"
        ]
        return self.create_appset_list_from_packages(go_packages, look_into_match="Go")

    def get_core_package(self):
        core_packages = [
            "com.google.android.gms",
            "com.android.vending",
            "com.google.android.gsf",
            "com.google.android.syncadapters.contacts",
            "com.google.android.syncadapters.calendar",
            "extra.files"
        ]
        package_list = []
        for package_name in core_packages:
            package = self.create_package(package_name)
            package.addon_index = "05"
            package_list.append(package)
        return self.create_appset_list(package_list)

    def get_basic_package(self, delta=False):
        basic_packages = [
            "com.google.android.apps.wellbeing",
            "com.google.android.apps.messaging",
            "com.google.android.dialer",
            "com.google.android.contacts",
            "com.google.android.ims",
            "com.google.android.deskclock"
        ]
        return (self.get_core_package() if not delta else []) + self.create_appset_list_from_packages(basic_packages)

    def get_omni_package(self, delta=False):
        setup_wizard_packages = [
            "com.google.android.setupwizard",
            "com.google.android.apps.restore",
            "com.google.android.onetimeinitializer"
        ]
        if float(self.android_version) < 12:
            setup_wizard_packages.append("com.google.android.apps.pixelmigrate")
        setup_wizard = self.create_appset_list_from_packages(setup_wizard_packages)
        omni_packages = [
            "com.google.android.calculator",
            "com.google.android.apps.docs",
            "com.google.android.apps.maps",
        ]
        if float(self.android_version) >= 11:
            omni_packages.append("com.google.android.gms.location.history")
        omni_packages.extend([
            "com.google.android.apps.photos",
            "com.google.android.apps.turbo",
            "com.google.android.inputmethod.latin",
            "com.google.android.calendar",
            "com.google.android.keep"
        ])
        return ((self.get_basic_package() if not delta else [])
                + setup_wizard
                + self.create_appset_list_from_packages(omni_packages))

    def get_stock_package(self, delta=False):
        pixel_launcher_packages = [
            "com.google.android.apps.nexuslauncher",
            "com.google.android.as",
            "com.google.android.apps.wallpaper"
        ]
        if float(self.android_version) >= 11:
            pixel_launcher_packages.append("com.android.systemui.plugin.globalactions.wallet")
            if float(self.android_version) >= 12:
                pixel_launcher_packages.extend(["com.google.android.settings.intelligence", "com.google.android.as.oss"])
                if float(self.android_version) >= 13:
                    pixel_launcher_packages.append("com.google.android.apps.customization.pixel")
                    if float(self.android_version) > 14:
                        pixel_launcher_packages.append("com.google.android.wallpaper.effects")
                    if float(self.android_version) >= 14:
                        pixel_launcher_packages.append("com.google.android.apps.weather")
        pixel_specifics = self.create_appset_list_from_packages(pixel_launcher_packages)
        stock_packages = [
            "com.google.android.play.games",
            "com.google.android.apps.recorder",
            "com.google.android.apps.nbu.files"
        ]
        if float(self.android_version) >= 11:
            stock_packages.append("com.google.android.documentsui")
        stock_packages.extend([
            "com.google.android.markup",
            "com.google.android.tts",
            "com.google.android.googlequicksearchbox",
            "com.google.android.soundpicker"
        ])
        return ((self.get_omni_package() if not delta else [])
                + pixel_specifics
                + self.create_appset_list_from_packages(stock_packages))

    def get_full_package(self, delta=False):
        full_packages = [
            "com.android.chrome",
            "com.google.android.webview",
            "com.google.android.trichromelibrary",
            "com.google.android.gm",
            "com.google.android.apps.work.oobconfig",
            "com.google.android.projection.gearhead",
            "com.google.android.feedback",
            "com.google.android.partnersetup",
            "com.google.android.apps.work.clouddpc"
        ]
        return (self.get_stock_package() if not delta else []) + self.create_appset_list_from_packages(full_packages)

    def get_addon_packages(self, addon_name=None):
        addon_packages = [
            "com.google.android.apps.tachyon",
            "com.google.android.apps.docs.editors.docs",
            "com.google.android.apps.docs.editors.sheets",
            "com.google.android.apps.docs.editors.slides",
            "com.google.android.youtube",
            "com.google.android.apps.youtube.music",
            "com.google.android.apps.books",
            "com.google.android.marvin.talkback",
        ]
        if float(self.android_version) == 11:
            addon_packages.append("com.google.android.apps.tycho")
        if float(self.android_version) == 13:
            addon_packages.append("com.google.android.apps.wallpaper.pixel")
        pixel_setup_wizard_packages = [
            "com.google.android.setupwizard",
            "com.google.android.apps.restore",
            "com.google.android.pixel.setupwizard",
            "com.google.android.onetimeinitializer"
        ]
        if float(self.android_version) < 12:
            pixel_setup_wizard_packages.append("com.google.android.apps.pixelmigrate")
        pixel_setup_wizard = self.create_appset_list_from_packages(pixel_setup_wizard_packages, look_into_match="Pixel")
        addon_set_list = pixel_setup_wizard + self.create_appset_list_from_packages(addon_packages)
        if addon_name:
            return [app_set for app_set in addon_set_list if app_set.title == addon_name]
        return addon_set_list

    def get_all_packages(self):
        all_package_list = []
        for app_set in self.get_full_package():
            all_package_list.append(app_set)
        for app_set in self.get_go_package():
            all_package_list.append(app_set)
        for app_set in self.get_addon_packages():
            all_package_list.append(app_set)
        return all_package_list

    def get_addonsets(self):
        addon_set_list = []
        for app_set in self.get_full_package():
            if app_set.title in ['Core', 'Pixelize']:
                continue
            addon_set_list.append(app_set)
        for app_set in self.get_go_package():
            if app_set.title in ['CoreGo']:
                continue
            addon_set_list.append(app_set)
        return addon_set_list
