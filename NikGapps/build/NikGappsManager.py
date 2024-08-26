import os

from NikGapps.build.PackageConstants import PackageConstants
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.Assets import Assets
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

        self.cmd = Cmd()
        self.package_data = Assets.package_details
        self.appset_data = Assets.appsets_details
        self.extra_files_exceptions = {
            "extra.files": "ExtraFiles",
            "extra.files.go": "ExtraFilesGo",
            "ExtraFiles": "extra.files",
            "ExtraFilesGo": "extra.files.go"
        }
        self.extra_files_appsets = {
            "extra.files": "Core",
            "extra.files.go": "CoreGo"
        }

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
            for app_set in self.get_addon_packages():
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

    def find_appset_by_package(self, package_title, keyword=None, fallback_appset=None):
        matched_appsets = []

        for appset, versions in self.appset_data.items():
            for version_info in versions:
                min_version = version_info.get("min_version", -1)
                max_version = version_info.get("max_version", float('inf'))
                exact_version = version_info.get("exact_version", None)
                packages = version_info["packages"]

                if exact_version is not None:
                    if self.android_version == exact_version and package_title in packages:
                        matched_appsets.append(appset)

                if float(min_version) <= float(self.android_version) <= float(
                        max_version) and package_title in packages:
                    matched_appsets.append(appset)

        if not matched_appsets:
            return None

        if keyword:
            for appset in matched_appsets:
                if keyword.lower() in appset.lower():
                    return appset

        if fallback_appset and fallback_appset in matched_appsets:
            return fallback_appset

        return matched_appsets[0]

    def create_appset_list(self, package_list, keyword=None, fallback_appset=None):
        appset_dict = {}
        for package in package_list:
            appset_title = self.find_appset_by_package(package.package_title, keyword=keyword, fallback_appset=fallback_appset)
            if appset_title not in appset_dict:
                appset_dict[appset_title] = AppSet(appset_title, [package])
            else:
                appset_dict[appset_title].package_list.append(package)
        return list(appset_dict.values())

    def create_appset_list_from_packages(self, package_name_list, keyword=None, fallback_appset=None):
        appset_dict = {}
        for package_name in package_name_list:
            package = self.create_package(package_name)
            appset_title = self.find_appset_by_package(package_name, keyword=keyword, fallback_appset=fallback_appset)
            if appset_title not in appset_dict:
                appset_dict[appset_title] = AppSet(appset_title, [package])
            else:
                appset_dict[appset_title].package_list.append(package)
        return list(appset_dict.values())

    def create_package(self, package_name):
        if package_name in self.extra_files_exceptions:
            package = Package(
                title=package_name,
                package_name=self.extra_files_exceptions[package_name],
            )
        else:
            package_details = self.get_package_details(package_name)
            package_info = package_details[0]
            pkg_name = package_info['package_name']
            package = Package(
                title=package_info['title'],
                package_name=pkg_name,
                app_type=Statics.is_priv_app if package_info['type'] == "priv-app" else Statics.is_system_app,
                package_title=package_name,
                partition=package_info['partition'] if float(self.android_version) > 10 else "product"
            )
            if float(self.android_version) > 12:
                overlays = self.get_package_overlays(pkg_name)
                for overlay in overlays:
                    package.add_overlay(overlay)
            deletes = PackageConstants.get_package_deletes(pkg_name)
            for delete in deletes:
                package.delete(delete)
            package.clean_flash_only = PackageConstants.get_package_clean_flash_rule(pkg_name)
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
            "ExtraFilesGo",
            "GmsCore",
            "GooglePlayStore",
            "GoogleServicesFramework",
            "GoogleContactsSyncAdapter",
            "GoogleCalendarSyncAdapter",
            "GoogleGo",
            "AssistantGo",
            "MapsGo",
            "NavigationGo",
            "GalleryGo",
            "GmailGo"
        ]
        appset_list = self.create_appset_list_from_packages(go_packages, keyword="Go")
        return appset_list

    def get_core_package(self):
        core_packages = [
            "ExtraFiles",
            "GooglePlayStore",
            "GoogleServicesFramework",
            "GoogleContactsSyncAdapter",
            "GoogleCalendarSyncAdapter",
            "GmsCore"
        ]
        package_list = []
        for package_title in core_packages:
            package = self.create_package(package_title)
            package.addon_index = "05"
            package_list.append(package)
        return self.create_appset_list(package_list)

    def get_basic_package(self, delta=False):
        basic_packages = [
            "DigitalWellbeing",
            "GoogleMessages",
            "GoogleDialer",
            "GoogleContacts",
            "CarrierServices",
            "GoogleClock"
        ]
        appset_list = (self.get_core_package() if not delta else []) + self.create_appset_list_from_packages(
            basic_packages)
        return appset_list

    def get_omni_package(self, delta=False):
        setup_wizard_packages = [
            "SetupWizard",
            "GoogleRestore",
            "GoogleOneTimeInitializer"
        ]
        if float(self.android_version) < 12:
            setup_wizard_packages.append("AndroidMigratePrebuilt")
        setup_wizard = self.create_appset_list_from_packages(setup_wizard_packages, fallback_appset="SetupWizard")
        omni_packages = [
            "GoogleCalculator",
            "Drive",
            "GoogleMaps",
        ]
        if float(self.android_version) >= 11:
            omni_packages.append("GoogleLocationHistory")
        omni_packages.extend([
            "GooglePhotos",
            "DeviceHealthServices",
            "GBoard",
            "GoogleCalendar",
            "GoogleKeep"
        ])
        appset_list = ((self.get_basic_package() if not delta else [])
                       + setup_wizard
                       + self.create_appset_list_from_packages(omni_packages))
        return appset_list

    def get_stock_package(self, delta=False):
        pixel_launcher_packages = [
            "PixelLauncher",
            "DevicePersonalizationServices",
            "GoogleWallpaper"
        ]
        if float(self.android_version) >= 11:
            pixel_launcher_packages.append("QuickAccessWallet")
            if float(self.android_version) >= 12:
                pixel_launcher_packages.extend([
                    "SettingsServices",
                    "PrivateComputeServices"
                ])
                if float(self.android_version) >= 13:
                    pixel_launcher_packages.append("PixelThemes")
                    if float(self.android_version) >= 14:
                        # pixel_launcher_packages.append("CinematicEffect")
                        pixel_launcher_packages.append("EmojiWallpaper")
                        pixel_launcher_packages.append("PixelWeather")
        pixel_specifics = self.create_appset_list_from_packages(pixel_launcher_packages)
        stock_packages = [
            "PlayGames",
            "GoogleRecorder",
            "GoogleFiles",
            "StorageManager"
        ]
        if float(self.android_version) >= 11:
            stock_packages.append("DocumentsUIGoogle")
        stock_packages.extend([
            "MarkupGoogle",
            "GoogleTTS",
            "Velvet",
            "Assistant",
            "GoogleSounds"
        ])
        return ((self.get_omni_package() if not delta else [])
                + pixel_specifics
                + self.create_appset_list_from_packages(stock_packages))

    def get_full_package(self, delta=False):
        full_packages = [
            "GoogleChrome",
            "WebViewGoogle",
            "TrichromeLibrary",
            "Gmail",
            "DeviceSetup",
            "AndroidAuto",
            "GoogleFeedback",
            "GooglePartnerSetup",
            "AndroidDevicePolicy"
        ]
        return (self.get_stock_package() if not delta else []) + self.create_appset_list_from_packages(full_packages)

    def get_addon_packages(self, addon_name=None):
        addon_packages = [
            "Meet",
            "GoogleDocs",
            "GoogleSheets",
            "GoogleSlides",
            "YouTube",
            "YouTubeMusic",
            "Books",
            "GoogleTalkback",
        ]
        if float(self.android_version) == 11:
            google_fi_packages = [
                "Tycho",
                "GCS"
            ]
            addon_packages.extend(google_fi_packages)
        # if float(self.android_version) == 13:
        #     addon_packages.append("PixelWallpapers")
        pixel_setup_wizard_packages = [
            "SetupWizard",
            "GoogleRestore",
            "PixelSetupWizard",
            "GoogleOneTimeInitializer"
        ]
        if float(self.android_version) < 12:
            pixel_setup_wizard_packages.append("AndroidMigratePrebuilt")
        pixel_setup_wizard = self.create_appset_list_from_packages(pixel_setup_wizard_packages, keyword="Pixel")
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
