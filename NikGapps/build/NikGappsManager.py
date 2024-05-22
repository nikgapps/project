import json
import os
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

        package = Package(
            title=package_info['title'],
            package_name=package_name,
            app_type=Statics.is_priv_app if package_info['type'] == "priv-app" else Statics.is_system_app,
            package_title=package_info['title']
        )

        overlays = self.get_package_overlays(package_name)
        for overlay in overlays:
            package.add_overlay(overlay)

        deletes = self.get_package_deletes(package_name)
        for delete in deletes:
            package.delete(delete)

        script = self.get_package_script(package_name)
        if script:
            package.additional_installer_script = script

        return package

    def get_package_overlays(self, package_name):
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
        return [Overlay(package_name, overlay["package_name"], self.android_version, overlay["resources"]) for overlay in package_overlays.get(package_name, [])]

    def get_package_deletes(self, package_name):
        package_deletes = {
            "com.google.android.gms": ["PrebuiltGmsCoreQt", "PrebuiltGmsCoreRvc", "GmsCore"],
            "com.google.android.dialer": ["Dialer"],
            "com.google.android.contacts": ["Contacts"],
            "com.google.android.tts": ["PicoTts"],
            "com.google.android.inputmethod.latin": ["LatinIME"],
            "com.google.android.calendar": ["Calendar", "Etar", "SimpleCalendar"],
            "com.google.android.apps.messaging": ["RevengeMessages", "messaging", "Messaging", "QKSMS", "Mms"],
            "com.google.android.apps.photos": ["Gallery", "SimpleGallery", "Gallery2", "MotGallery", "MediaShortcuts", "SimpleGallery", "FineOSGallery", "GalleryX", "MiuiGallery", "SnapdragonGallery", "DotGallery", "Glimpse"],
            "com.google.android.keep": ["Notepad"],
            "com.google.android.apps.recorder": ["Recorder", "QtiSoundRecorder"],
            "com.google.android.gm": ["Email", "PrebuiltEmailGoogle"],
            "com.google.android.apps.wallpaper": ["Wallpapers"],
            "com.android.chrome": ["Bolt", "Browser", "Browser2", "BrowserIntl", "BrowserProviderProxy", "Chromium", "DuckDuckGo", "Fluxion", "Gello", "Jelly", "PA_Browser", "PABrowser", "YuBrowser", "BLUOpera", "BLUOperaPreinstall", "ViaBrowser", "Duckduckgo"],
            "com.google.android.youtube.music": ["SnapdragonMusic", "GooglePlayMusic", "Eleven", "CrDroidMusic"],
            "com.google.android.setupwizard": ["Provision", "SetupWizard", "LineageSetupWizard"]
        }
        return package_deletes.get(package_name, [])

    def get_package_script(self, package_name):
        package_scripts = {
            "com.google.android.gms": """
gms_optimization=$(ReadConfigValue "GmsOptimization" "$nikgapps_config_file_name")
[ -z "$gms_optimization" ] && gms_optimization=0
if [ "$gms_optimization" = "1" ]; then
    sed -i '/allow-in-power-save package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
    sed -i '/allow-in-data-usage-save package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
    sed -i '/allow-unthrottled-location package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
    sed -i '/allow-ignore-location-settings package=\"com.google.android.gms\"/d' $install_partition/etc/permissions/*.xml
    addToLog \"- Battery Optimization Done in $install_partition/etc/permissions/*.xml!\" "$package_title"
    sed -i '/allow-in-power-save package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
    sed -i '/allow-in-data-usage-save package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
    sed -i '/allow-unthrottled-location package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
    sed -i '/allow-ignore-location-settings package=\"com.google.android.gms\"/d' $install_partition/etc/sysconfig/*.xml
    addToLog \"- Battery Optimization Done in $install_partition/etc/sysconfig/*.xml!\" "$package_title"
else
    addToLog "- Battery Optimization not Enabled" "$package_title"
fi
    """,
            "com.google.android.dialer": """
   script_text="<permissions>
    <!-- Shared library required on the device to get Google Dialer updates from
         Play Store. This will be deprecated once Google Dialer play store
         updates stop supporting pre-O devices. -->
    <library name=\\"com.google.android.dialer.support\\"
      file=\\"$install_partition/framework/com.google.android.dialer.support.jar\\" />

    <!-- Starting from Android O and above, this system feature is required for
         getting Google Dialer play store updates. -->
    <feature name=\\"com.google.android.apps.dialer.SUPPORTED\\" />
    <!-- Feature for Google Dialer Call Recording -->
    <feature name=\\"com.google.android.apps.dialer.call_recording_audio\\" />
</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.dialer.support.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.dialer.support.xml"
   update_prop "$install_partition/etc/permissions/com.google.android.dialer.support.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.android.dialer.support.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.android.dialer.support.xml Successfully Written!" "$package_title"
   fi""",
            "com.google.android.maps": """
   script_text="<permissions>
    <library name=\\"com.google.android.maps\\"
            file=\\"$install_partition/framework/com.google.android.maps.jar\\" />
</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.maps.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.maps.xml"
   update_prop "$install_partition/etc/permissions/com.google.android.maps.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.android.maps.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.android.maps.xml Successfully Written!" "$package_title"
   fi""",
            "com.google.android.media.effects": """
   script_text="<permissions>
<library name=\\"com.google.android.media.effects\\"
file=\\"$install_partition/framework/com.google.android.media.effects.jar\\" />

</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.media.effects.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.media.effects.xml"
   update_prop "$install_partition/etc/permissions/com.google.android.media.effects.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.android.media.effects.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.android.media.effects.xml Successfully Written!" "$package_title"
   fi""",
            "com.google.android.settings.intelligence": """
   set_prop "setupwizard.feature.baseline_setupwizard_enabled" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.setupwizard.enterprise_mode" "1" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.setupwizard.rotation_locked" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.enable_assist_gesture_training" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.theme" "glif_v3_light" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.skip_button_use_mobile_data.carrier1839" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.show_pai_screen_in_main_flow.carrier1839" "false" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.show_pixel_tos" "false" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.show_digital_warranty" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.setupwizard.esim_cid_ignore" "00000001" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.setupwizard.setupwizard.feature.show_support_link_in_deferred_setup" "false" "$product/etc/build.prop" "$package_title"
   set_prop "setupwizard.feature.enable_wifi_tracker" "true" "$product/etc/build.prop" "$package_title"
   set_prop "setupwizard.feature.day_night_mode_enabled" "true" "$product/etc/build.prop" "$package_title"
   set_prop "setupwizard.feature.portal_notification" "true" "$product/etc/build.prop" "$package_title"
   set_prop "setupwizard.feature.lifecycle_refactoring" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.notification_refactoring" "true" "$product/etc/build.prop" "$package_title"
    """,
            "com.google.android.googlequicksearchbox": """
   set_prop "ro.opa.eligible_device" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
    """
        }
        return package_scripts.get(package_name, None)

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
            "com.google.android.ims",
            "com.google.android.deskclock"
        ]

        for package_name in basic_packages:
            package = self.create_package(package_name)
            app_set_list.append(AppSet(package.package_title, [package]))

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