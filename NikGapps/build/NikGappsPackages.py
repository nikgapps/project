from NikGapps.helper import Config
from NikGapps.helper.Statics import Statics
from NikGapps.helper.Package import Package
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.overlay.Library import Library
from NikGapps.helper.overlay.Overlay import Overlay


class NikGappsPackages:
    all_packages = "full"

    @staticmethod
    def get_packages(package_type, android_version):
        if str(package_type).lower() == "go":
            return NikGappsPackages.get_go_package(android_version)
        if str(package_type).lower() == "core":
            return NikGappsPackages.get_core_package(android_version)
        if str(package_type).lower() == "basic":
            return NikGappsPackages.get_basic_package(android_version)
        if str(package_type).lower() == "omni":
            return NikGappsPackages.get_omni_package(android_version)
        if str(package_type).lower() == "stock":
            return NikGappsPackages.get_stock_package(android_version)
        if str(package_type).lower() == "full":
            return NikGappsPackages.get_full_package(android_version)
        if str(package_type).lower() == "all":
            all_package_list = []
            for app_set in NikGappsPackages.get_full_package(android_version):
                all_package_list.append(app_set)
            for app_set in NikGappsPackages.get_go_package(android_version):
                all_package_list.append(app_set)
            for app_set in NikGappsPackages.get_addon_packages(android_version):
                all_package_list.append(app_set)
            return all_package_list
        if str(package_type).lower() == "addons":
            addon_set_list = NikGappsPackages.get_addon_packages(android_version)
            return addon_set_list
        if str(package_type).lower() == "addonsets":
            addon_set_list = []
            for app_set in NikGappsPackages.get_full_package(android_version):
                if app_set.title in ['Core', 'Pixelize']:
                    continue
                addon_set_list.append(app_set)
            for app_set in NikGappsPackages.get_go_package(android_version):
                if app_set.title in ['CoreGo']:
                    continue
                addon_set_list.append(app_set)
            return addon_set_list
        else:
            addon_set_list = NikGappsPackages.get_addon_packages(android_version, package_type)
            if addon_set_list is None:
                for app_set in NikGappsPackages.get_full_package(android_version):
                    if str(app_set.title).lower() == str(package_type).lower():
                        return [app_set]
                    elif len(app_set.package_list) > 1:
                        for package in app_set.package_list:
                            if str(package.package_title).lower() == str(package_type).lower():
                                return [AppSet(app_set.title, [package])]
                for app_set in NikGappsPackages.get_go_package(android_version):
                    if str(app_set.title).lower() == str(package_type).lower():
                        return [app_set]
                    elif len(app_set.package_list) > 1:
                        for package in app_set.package_list:
                            if str(package.package_title).lower() == str(package_type).lower():
                                return [AppSet(app_set.title, [package])]
                return [None]
            else:
                return addon_set_list

    @staticmethod
    def get_app_set(pkg: Package, title=None):
        if title is None:
            name = pkg.package_title
        else:
            name = title
        return AppSet(name, [pkg])

    @staticmethod
    def get_go_package(android_version):
        extra_files_go = Package("ExtraFilesGo", None, None)
        extra_files_go.additional_installer_script = """   script_text="<permissions>
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
   fi"""
        extra_files_go.additional_installer_script += """
   script_text="<permissions>
    <library name=\\"com.google.android.maps\\"
            file=\\"$install_partition/framework/com.google.android.maps.jar\\" />
</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.maps.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.maps.xml"
   update_prop "$install_partition/etc/permissions/com.google.android.maps.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.android.maps.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.android.maps.xml Successfully Written!" "$package_title"
   fi"""
        extra_files_go.additional_installer_script += """
   script_text="<permissions>
<library name=\\"com.google.widevine.software.drm\\"
file=\\"/system/product/framework/com.google.widevine.software.drm.jar\\"/>
</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.widevine.software.drm.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.widevine.software.drm.xml"
   update_prop "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.widevine.software.drm.xml Successfully Written!" "$package_title"
   fi"""
        extra_files_go.additional_installer_script += """
   script_text="<permissions>
<library name=\\"com.google.android.media.effects\\"
file=\\"$install_partition/framework/com.google.android.media.effects.jar\\" />

</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.media.effects.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.media.effects.xml"
   update_prop "$install_partition/etc/permissions/com.google.android.media.effects.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.android.media.effects.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.android.media.effects.xml Successfully Written!" "$package_title"
   fi"""

        core_go = AppSet("CoreGo")
        core_go.add_package(extra_files_go)

        prebuiltgmscore = Package("PrebuiltGmsCore", "com.google.android.gms", Statics.is_priv_app, "GmsCore")
        if float(android_version) >= 12.1:
            prebuiltgmscore_overlay = Overlay(prebuiltgmscore.package_title, "com.nikgapps.overlay.gmscore",
                                              android_version, Library.get_gms_core_resources())
            prebuiltgmscore.add_overlay(prebuiltgmscore_overlay)
        prebuiltgmscore.delete("PrebuiltGmsCoreQt")
        prebuiltgmscore.delete("PrebuiltGmsCoreRvc")
        prebuiltgmscore.delete("GmsCore")
        prebuiltgmscore.additional_installer_script = """
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
    """
        core_go.add_package(prebuiltgmscore)

        phonesky = Package("Phonesky", "com.android.vending", Statics.is_priv_app, "GooglePlayStore")
        core_go.add_package(phonesky)

        googleservicesframework = Package("GoogleServicesFramework", "com.google.android.gsf", Statics.is_priv_app)
        core_go.add_package(googleservicesframework)

        googlecontactssyncadapter = Package("GoogleContactsSyncAdapter", "com.google.android.syncadapters.contacts",
                                            Statics.is_system_app)
        core_go.add_package(googlecontactssyncadapter)

        googlecalendarsync = Package("GoogleCalendarSyncAdapter", "com.google.android.syncadapters.calendar",
                                     Statics.is_system_app)
        core_go.add_package(googlecalendarsync)
        for pkg in core_go.package_list:
            pkg.addon_index = "05"
        app_set_list = [core_go]

        google_go = Package("GoogleGo", "com.google.android.apps.searchlite", Statics.is_priv_app)
        app_set_list.append(AppSet("GoogleGo", [google_go]))

        google_assistant_go = Package("AssistantGo", "com.google.android.apps.assistant", Statics.is_priv_app)
        app_set_list.append(AppSet("AssistantGo", [google_assistant_go]))

        google_maps_go = Package("MapsGo", "com.google.android.apps.mapslite", Statics.is_system_app)
        app_set_list.append(AppSet("MapsGo", [google_maps_go]))

        navigation_go = Package("NavigationGo", "com.google.android.apps.navlite", Statics.is_system_app)
        app_set_list.append(AppSet("NavigationGo", [navigation_go]))

        gallery_go = Package("GalleryGo", "com.google.android.apps.photosgo", Statics.is_system_app)
        app_set_list.append(AppSet("GalleryGo", [gallery_go]))

        gmail_go = Package("GmailGo", "com.google.android.gm.lite", Statics.is_system_app)
        app_set_list.append(AppSet("GmailGo", [gmail_go]))

        return app_set_list

    @staticmethod
    def get_core_package(android_version):
        files = Package("ExtraFiles", None, None)
        files.additional_installer_script = """   script_text="<permissions>
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
   fi"""
        files.additional_installer_script += """
   script_text="<permissions>
    <library name=\\"com.google.android.maps\\"
            file=\\"$install_partition/framework/com.google.android.maps.jar\\" />
</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.maps.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.maps.xml"
   update_prop "$install_partition/etc/permissions/com.google.android.maps.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.android.maps.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.android.maps.xml Successfully Written!" "$package_title"
   fi"""
        files.additional_installer_script += """
   script_text="<permissions>
<library name=\\"com.google.widevine.software.drm\\"
file=\\"/system/product/framework/com.google.widevine.software.drm.jar\\"/>
</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.widevine.software.drm.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.widevine.software.drm.xml"
   update_prop "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.widevine.software.drm.xml Successfully Written!" "$package_title"
   fi"""
        files.additional_installer_script += """
   script_text="<permissions>
<library name=\\"com.google.android.media.effects\\"
file=\\"$install_partition/framework/com.google.android.media.effects.jar\\" />

</permissions>"
   echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.media.effects.xml
   set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.media.effects.xml"
   update_prop "$install_partition/etc/permissions/com.google.android.media.effects.xml" "install" "$propFilePath" "$package_title"
   if [ -f "$install_partition/etc/permissions/com.google.android.media.effects.xml" ]; then
     addToLog "- $install_partition/etc/permissions/com.google.android.media.effects.xml Successfully Written!" "$package_title"
   fi"""

        prebuiltgmscore = Package("PrebuiltGmsCore", "com.google.android.gms", Statics.is_priv_app, "GmsCore")
        if float(android_version) >= 12.1:
            prebuiltgmscore_overlay = Overlay(prebuiltgmscore.package_title, "com.nikgapps.overlay.gmscore",
                                              android_version, Library.get_gms_core_resources())
            prebuiltgmscore.add_overlay(prebuiltgmscore_overlay)
        prebuiltgmscore.delete("PrebuiltGmsCoreQt")
        prebuiltgmscore.delete("PrebuiltGmsCoreRvc")
        prebuiltgmscore.delete("GmsCore")
        prebuiltgmscore.additional_installer_script = """
gms_optimization=$(ReadConfigValue "gms_optimization" "$nikgapps_config_file_name")
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
            """
        phonesky = Package("Phonesky", "com.android.vending", Statics.is_priv_app, "GooglePlayStore")
        googleservicesframework = Package("GoogleServicesFramework", "com.google.android.gsf", Statics.is_priv_app)
        googlecontactssyncadapter = Package("GoogleContactsSyncAdapter", "com.google.android.syncadapters.contacts",
                                            Statics.is_system_app)
        googlecalendarsync = Package("GoogleCalendarSyncAdapter", "com.google.android.syncadapters.calendar",
                                     Statics.is_system_app)
        gapps_list = [files, phonesky, googleservicesframework, googlecontactssyncadapter, googlecalendarsync,
                      prebuiltgmscore]
        for pkg in gapps_list:
            pkg.addon_index = "05"
        return [AppSet("Core", gapps_list)]

    @staticmethod
    def get_basic_package(android_version):
        app_set_list = NikGappsPackages.get_core_package(android_version)
        digital_wellbeing = Package("WellbeingPreBuilt", "com.google.android.apps.wellbeing", Statics.is_priv_app,
                                    "DigitalWellbeing")
        if float(android_version) >= 12.1:
            digital_wellbeing_overlay = Overlay(apk_name=digital_wellbeing.package_title,
                                                package_name="com.nikgapps.overlay.wellbeing",
                                                android_version=android_version,
                                                resources=Library.get_digital_wellbeing_resources())
            digital_wellbeing.overlay_list.append(digital_wellbeing_overlay)
        app_set_list.append(AppSet("DigitalWellbeing", [digital_wellbeing]))
        google_messages = Package("PrebuiltBugle", "com.google.android.apps.messaging", Statics.is_priv_app,
                                  "GoogleMessages")
        if float(android_version) >= 12.1:
            google_messages_overlay = Overlay(apk_name=google_messages.package_title,
                                              package_name="com.nikgapps.overlay.messages",
                                              android_version=android_version,
                                              resources=Library.get_google_messages_resources())
            google_messages.overlay_list.append(google_messages_overlay)
        google_messages.delete("RevengeMessages")
        google_messages.delete("messaging")
        google_messages.delete("Messaging")
        google_messages.delete("QKSMS")
        google_messages.delete("Mms")
        app_set_list.append(AppSet("GoogleMessages", [google_messages]))

        google_dialer = Package("GoogleDialer", "com.google.android.dialer", Statics.is_priv_app)
        if float(android_version) >= 12.1:
            google_dialer_overlay = Overlay(apk_name=google_dialer.package_title,
                                            package_name="com.nikgapps.overlay.dialer",
                                            android_version=android_version,
                                            resources=Library.get_google_dialer_resources())
            google_dialer.add_overlay(google_dialer_overlay)
        google_dialer.predefined_file_list.append("framework/com.google.android.dialer.support.jar")
        google_dialer.delete("Dialer")
        app_set_list.append(AppSet("GoogleDialer", [google_dialer]))

        google_contacts = Package("GoogleContacts", "com.google.android.contacts", Statics.is_system_app)
        if float(android_version) >= 12.1:
            google_contacts_overlay = Overlay(apk_name=google_contacts.package_title,
                                              package_name="com.nikgapps.overlay.contacts",
                                              android_version=android_version,
                                              resources=Library.get_google_contacts_resources())
            google_contacts.add_overlay(google_contacts_overlay)
        google_contacts.delete("Contacts")
        app_set_list.append(AppSet("GoogleContacts", [google_contacts]))

        carrier_services = Package("CarrierServices", "com.google.android.ims", Statics.is_priv_app)
        app_set_list.append(AppSet("CarrierServices", [carrier_services]))
        app_set_list.append(NikGappsPackages.get_google_clock(android_version))
        return app_set_list

    @staticmethod
    def get_omni_package(android_version):
        app_set_list = NikGappsPackages.get_basic_package(android_version)
        app_set_list.append(NikGappsPackages.get_setup_wizard(android_version))
        # Dropping pixelize support, need to keep it stock
        calculator = Package("CalculatorGooglePrebuilt", "com.google.android.calculator", Statics.is_system_app,
                             "GoogleCalculator")
        calculator.delete("ExactCalculator")
        calculator.delete("MotoCalculator")
        calculator.delete("RevengeOSCalculator")
        app_set_list.append(AppSet("GoogleCalculator", [calculator]))
        google_drive = Package("Drive", "com.google.android.apps.docs", Statics.is_system_app)
        app_set_list.append(AppSet("Drive", [google_drive]))
        google_maps = Package("GoogleMaps", "com.google.android.apps.maps", Statics.is_system_app)
        google_maps.delete("Maps")
        app_set_list.append(AppSet("GoogleMaps", [google_maps]))
        if float(android_version) >= 11:
            google_location_history = Package("LocationHistoryPrebuilt", "com.google.android.gms.location.history",
                                              Statics.is_system_app, "GoogleLocationHistory")
            if float(android_version) >= 12.1:
                google_location_history_overlay = Overlay(apk_name=google_location_history.package_title,
                                                          package_name="com.nikgapps.overlay.googlelocationhistory",
                                                          android_version=android_version,
                                                          resources=Library.get_google_location_history_resources())
                google_location_history.add_overlay(google_location_history_overlay)
            app_set_list.append(AppSet("GoogleLocationHistory", [google_location_history]))
        google_photos = Package("Photos", "com.google.android.apps.photos", Statics.is_system_app, "GooglePhotos")
        if float(android_version) >= 12.1:
            google_photos_overlay = Overlay(apk_name=google_photos.package_title,
                                            package_name="com.nikgapps.overlay.googlephotos",
                                            android_version=android_version,
                                            resources=Library.get_google_photos_resources())
            google_photos.add_overlay(google_photos_overlay)
        google_photos.delete("Gallery")
        google_photos.delete("SimpleGallery")
        google_photos.delete("Gallery2")
        google_photos.delete("MotGallery")
        google_photos.delete("MediaShortcuts")
        google_photos.delete("SimpleGallery")
        google_photos.delete("FineOSGallery")
        google_photos.delete("GalleryX")
        google_photos.delete("MiuiGallery")
        google_photos.delete("SnapdragonGallery")
        google_photos.delete("DotGallery")
        google_photos.delete("Glimpse")
        app_set_list.append(AppSet("GooglePhotos", [google_photos]))
        google_turbo = Package("Turbo", "com.google.android.apps.turbo", Statics.is_priv_app, "DeviceHealthServices")
        google_turbo.delete("TurboPrebuilt")
        app_set_list.append(AppSet("DeviceHealthServices", [google_turbo]))
        google_board = Package("LatinIMEGooglePrebuilt", "com.google.android.inputmethod.latin",
                               Statics.is_system_app, "GBoard")
        google_board.additional_installer_script = """
   set_prop "ro.com.google.ime.theme_id" "5" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.com.google.ime.kb_pad_port_b" "8" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.com.google.ime.height_ratio" "1.025" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.com.google.ime.system_lm_dir" "$install_partition/usr/share/ime/google/d3_lms" "$product/etc/build.prop" "$propFilePath" "$package_title"
             """
        google_board.delete("LatinIME")
        google_board.clean_flash_only = True
        app_set_list.append(AppSet("GBoard", [google_board]))
        google_calendar = Package("CalendarGooglePrebuilt", "com.google.android.calendar", Statics.is_system_app,
                                  "GoogleCalendar")
        google_calendar.delete("Calendar")
        google_calendar.delete("Etar")
        google_calendar.delete("SimpleCalendar")
        app_set_list.append(AppSet("GoogleCalendar", [google_calendar]))
        google_keep = Package("PrebuiltKeep", "com.google.android.keep", Statics.is_priv_app, "GoogleKeep")
        google_keep.delete("Notepad")
        app_set_list.append(AppSet("GoogleKeep", [google_keep]))
        return app_set_list

    @staticmethod
    def get_stock_package(android_version):
        app_set_list = NikGappsPackages.get_omni_package(android_version)
        play_games = Package("PlayGames", "com.google.android.play.games", Statics.is_system_app)
        app_set_list.append(AppSet("PlayGames", [play_games]))
        app_set_list.append(NikGappsPackages.get_pixel_launcher(android_version))
        google_recorder = Package("RecorderPrebuilt", "com.google.android.apps.recorder", Statics.is_priv_app,
                                  "GoogleRecorder")
        google_recorder.delete("Recorder")
        google_recorder.delete("QtiSoundRecorder")
        app_set_list.append(AppSet("GoogleRecorder", [google_recorder]))
        app_set_list.append(NikGappsPackages.get_google_files(android_version))
        google_markup = Package("MarkupGoogle", "com.google.android.markup", Statics.is_system_app)
        app_set_list.append(AppSet("MarkupGoogle", [google_markup]))
        app_set_list.append(NikGappsPackages.get_google_tts(android_version))
        google_velvet = Package("Velvet", "com.google.android.googlequicksearchbox", Statics.is_priv_app)
        if float(android_version) >= 12.1:
            google_velvet_overlay = Overlay(apk_name=google_velvet.package_title,
                                            package_name="com.nikgapps.overlay.googlequicksearchbox",
                                            android_version=android_version,
                                            resources=Library.get_velvet_resources())
            google_velvet.add_overlay(google_velvet_overlay)
        google_velvet.priv_app_permissions.append("android.permission.EXPAND_STATUS_BAR")
        google_velvet.priv_app_permissions.append("android.permission.SET_MEDIA_KEY_LISTENER")
        google_velvet.priv_app_permissions.append("android.permission.SET_VOLUME_KEY_LONG_PRESS_LISTENER")
        google_velvet.priv_app_permissions.append("android.permission.MANAGE_USB")
        google_velvet.priv_app_permissions.append("android.permission.START_ACTIVITIES_FROM_BACKGROUND")
        google_velvet.priv_app_permissions.append("android.permission.WRITE_APN_SETTINGS")
        google_velvet.priv_app_permissions.append("android.permission.BLUETOOTH_PRIVILEGED")
        google_velvet.priv_app_permissions.append("android.permission.MODIFY_AUDIO_ROUTING")
        google_velvet.clean_flash_only = True
        google_velvet.additional_installer_script = """
   set_prop "ro.opa.eligible_device" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
"""
        google_assistant = Package("Assistant", "com.google.android.apps.googleassistant", Statics.is_priv_app)
        google_assistant.clean_flash_only = True
        app_set_list.append(AppSet("GoogleSearch", [google_velvet, google_assistant]))
        google_sounds = Package("SoundPickerPrebuilt", "com.google.android.soundpicker", Statics.is_system_app,
                                "GoogleSounds")
        google_sounds.delete("SoundPicker")
        google_sounds.clean_flash_only = True
        app_set_list.append(AppSet("GoogleSounds", [google_sounds]))
        return app_set_list

    @staticmethod
    def get_full_package(android_version):
        app_set_list = NikGappsPackages.get_stock_package(android_version)
        app_set_list.append(NikGappsPackages.get_chrome(android_version))
        gmail = Package("PrebuiltGmail", "com.google.android.gm", Statics.is_system_app, "Gmail")
        gmail.delete("Email")
        gmail.delete("PrebuiltEmailGoogle")
        app_set_list.append(AppSet("Gmail", [gmail]))
        if float(android_version) >= 10:
            google_device_setup = Package("OTAConfigPrebuilt", "com.google.android.apps.work.oobconfig",
                                          Statics.is_priv_app, "DeviceSetup")
            app_set_list.append(AppSet("DeviceSetup", [google_device_setup]))
        android_auto = Package("AndroidAutoStubPrebuilt", "com.google.android.projection.gearhead",
                               Statics.is_priv_app, "AndroidAuto")
        android_auto.clean_flash_only = True
        if float(android_version) >= 12.1:
            android_auto_overlay = Overlay(apk_name=android_auto.package_title,
                                           package_name="com.nikgapps.overlay.androidauto",
                                           android_version=android_version,
                                           resources=Library.get_android_auto_resources())
            android_auto.add_overlay(android_auto_overlay)
        app_set_list.append(AppSet("AndroidAuto", [android_auto]))
        google_feedback = Package("GoogleFeedback", "com.google.android.feedback", Statics.is_priv_app,
                                  partition=Statics.get_partition(android_version, "system_ext"))
        app_set_list.append(AppSet("GoogleFeedback", [google_feedback]))
        google_partner_setup = Package("PartnerSetupPrebuilt", "com.google.android.partnersetup", Statics.is_priv_app,
                                       "GooglePartnerSetup")
        app_set_list.append(AppSet("GooglePartnerSetup", [google_partner_setup]))
        if float(android_version) >= 10:
            android_device_policy = Package("DevicePolicyPrebuilt", "com.google.android.apps.work.clouddpc",
                                            Statics.is_system_app, "AndroidDevicePolicy")
            app_set_list.append(AppSet("AndroidDevicePolicy", [android_device_policy]))

        return app_set_list

    @staticmethod
    def get_google_files(android_version):
        app_set_list = AppSet("GoogleFiles")
        google_files = Package("FilesPrebuilt", "com.google.android.apps.nbu.files", Statics.is_priv_app,
                               "GoogleFiles")
        app_set_list.add_package(google_files)
        storage_manager_google = Package("StorageManagerGoogle", "com.google.android.storagemanager",
                                         Statics.is_priv_app, "StorageManager",
                                         partition=Statics.get_partition(android_version, "system_ext"))
        storage_manager_google.delete("StorageManager")
        app_set_list.add_package(storage_manager_google)
        if float(android_version) >= 11:
            documents_ui_google = Package("DocumentsUIGoogle", "com.google.android.documentsui", Statics.is_priv_app)
            documents_ui_google.delete("DocumentsUI")
            app_set_list.add_package(documents_ui_google)
        return app_set_list

    @staticmethod
    def get_chrome(android_version):
        google_chrome = Package("GoogleChrome", "com.android.chrome", Statics.is_system_app)
        google_chrome.delete("Bolt")
        google_chrome.delete("Browser")
        google_chrome.delete("Browser2")
        google_chrome.delete("BrowserIntl")
        google_chrome.delete("BrowserProviderProxy")
        google_chrome.delete("Chromium")
        google_chrome.delete("DuckDuckGo")
        google_chrome.delete("Fluxion")
        google_chrome.delete("Gello")
        google_chrome.delete("Jelly")
        google_chrome.delete("PA_Browser")
        google_chrome.delete("PABrowser")
        google_chrome.delete("YuBrowser")
        google_chrome.delete("BLUOpera")
        google_chrome.delete("BLUOperaPreinstall")
        google_chrome.delete("ViaBrowser")
        google_chrome.delete("Duckduckgo")
        app_set_list = AppSet("GoogleChrome")
        app_set_list.add_package(google_chrome)
        if float(android_version) >= 10:
            google_webview = Package("WebViewGoogle", "com.google.android.webview", Statics.is_system_app)
            google_webview.delete("webview")
            trichromelibrary = Package("TrichromeLibrary", "com.google.android.trichromelibrary",
                                       Statics.is_system_app)
            app_set_list.add_package(google_webview)
            app_set_list.add_package(trichromelibrary)
        return app_set_list

    @staticmethod
    def get_setup_wizard(android_version):
        setup_wizard = Package("SetupWizardPrebuilt", "com.google.android.setupwizard", Statics.is_priv_app,
                               "SetupWizard")
        setup_wizard.delete("Provision")
        setup_wizard.delete("SetupWizard")
        setup_wizard.delete("LineageSetupWizard")
        setup_wizard.additional_installer_script = """
   set_prop "setupwizard.feature.baseline_setupwizard_enabled" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.setupwizard.enterprise_mode" "1" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "ro.setupwizard.rotation_locked" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.enable_assist_gesture_training" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.theme" "glif_v3_light" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.skip_button_use_mobile_data.carrier1839" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.show_pai_screen_in_main_flow.carrier1839" "false" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.show_pixel_tos" "false" "$product/etc/build.prop" "$propFilePath" "$package_title"
        """
        google_restore = Package("GoogleRestore", "com.google.android.apps.restore", Statics.is_priv_app)
        google_restore.delete("Seedvault")
        android_migrate_prebuilt = Package("AndroidMigratePrebuilt", "com.google.android.apps.pixelmigrate",
                                           Statics.is_priv_app)
        setup_wizard_set = AppSet("SetupWizard")
        setup_wizard_set.add_package(setup_wizard)
        setup_wizard_set.add_package(google_restore)
        if float(android_version) >= 10:
            google_one_time_initializer = Package("GoogleOneTimeInitializer", "com.google.android.onetimeinitializer",
                                                  Statics.is_priv_app,
                                                  partition=Statics.get_partition(android_version, "system_ext"))
            setup_wizard_set.add_package(google_one_time_initializer)
        if float(android_version) < 12:
            setup_wizard_set.add_package(android_migrate_prebuilt)
        return setup_wizard_set

    @staticmethod
    def get_addon_packages(android_version, addon_name=None):
        addon_set_list = [
            NikGappsPackages.get_google_duo(),
            NikGappsPackages.get_google_docs(),
            NikGappsPackages.get_google_slides(),
            NikGappsPackages.get_google_sheets(),
            NikGappsPackages.get_youtube(),
            NikGappsPackages.get_youtube_music(android_version),
            NikGappsPackages.get_google_play_books(),
            # AddonSet.get_google_tts(),
            NikGappsPackages.get_pixel_setup_wizard(android_version),
            NikGappsPackages.get_google_talkback(android_version)
        ]
        if float(android_version) == 11:
            addon_set_list.append(NikGappsPackages.get_google_fi())
        # if float(android_version) == float(12.1):
        #     addon_set_list.append(AddonSet.get_lawnchair())
        # if float(android_version) in (10, 11):
        #     addon_set_list.append(AddonSet.get_pixel_setup_wizard())
        # if float(android_version) >= 13:
        #     addon_set_list.append(NikGappsPackages.get_flipendo(android_version))
        if float(android_version) == 13:
            addon_set_list.append(NikGappsPackages.get_pixel_live_wallpapers(android_version))
        if addon_name is None:
            return addon_set_list
        else:
            for addon_set in addon_set_list:
                if addon_set.title == addon_name:
                    return [addon_set]
        return None

    @staticmethod
    def get_google_camera_go():
        google_camera_lite = Package("GoogleCameraGo", "com.google.android.apps.cameralite", Statics.is_system_app)
        return AppSet("GoogleCameraGo", [google_camera_lite])

    @staticmethod
    def get_google_clock(android_version):
        gapps_list = []
        google_clock = Package("PrebuiltDeskClockGoogle", "com.google.android.deskclock", Statics.is_system_app,
                               "GoogleClock")
        google_clock.delete("DeskClock")
        google_clock.clean_flash_only = True
        if float(android_version) >= 12.1:
            google_clock_overlay = Overlay(apk_name=google_clock.package_title,
                                           package_name="com.nikgapps.overlay.googleclock",
                                           android_version=android_version,
                                           resources=Library.get_google_clock_resources())
            google_clock.add_overlay(google_clock_overlay)
        gapps_list.append(google_clock)
        return AppSet("GoogleClock", gapps_list)

    @staticmethod
    def get_lineageos_recorder():
        los_recorder = Package("Recorder", "org.lineageos.recorder", Statics.is_system_app)
        return AppSet("Recorder", [los_recorder])

    @staticmethod
    def get_google_tts(android_version):
        google_tts = Package("GoogleTTS", "com.google.android.tts", Statics.is_system_app)
        if float(android_version) >= 12.1:
            google_tts_overlay = Overlay(google_tts.package_title, "com.nikgapps.overlay.googletts", android_version,
                                         Library.get_google_tts_resources())
            google_tts.add_overlay(google_tts_overlay)
        google_tts.delete("PicoTts")
        return AppSet("GoogleTTS", [google_tts])

    @staticmethod
    def get_google_talkback(android_version):
        talkback = Package("talkback", "com.google.android.marvin.talkback", Statics.is_system_app, "GoogleTalkback")
        if float(android_version) >= 12.1:
            talkback_overlay = Overlay(talkback.package_title, "com.nikgapps.overlay.talkback", android_version,
                                       Library.get_google_talkback_resources())
            talkback.add_overlay(talkback_overlay)
        return AppSet("GoogleTalkback", [talkback])

    @staticmethod
    def get_snap_camera():
        snap = Package("Snap", "org.lineageos.snap", Statics.is_priv_app)
        snap.delete("GoogleCameraGo")
        snap.delete("ScreenRecorder")
        return AppSet("Snap", [snap])

    @staticmethod
    def get_flipendo(android_version):
        flipendo = Package("Flipendo", "com.google.android.flipendo", Statics.is_system_app,
                           partition=Statics.get_partition(android_version, "system_ext"))
        if float(android_version) >= 12.1:
            flipendo_overlay = Overlay(flipendo.package_title, "com.nikgapps.overlay.flipendo", android_version,
                                       Library.get_flipendo_resources())
            flipendo.add_overlay(flipendo_overlay)
        return AppSet("Flipendo", [flipendo])

    @staticmethod
    def get_google_docs():
        google_docs = Package("GoogleDocs", "com.google.android.apps.docs.editors.docs", Statics.is_system_app)
        return AppSet("GoogleDocs", [google_docs])

    @staticmethod
    def get_google_sheets():
        google_sheets = Package("GoogleSheets", "com.google.android.apps.docs.editors.sheets", Statics.is_system_app)
        return AppSet("GoogleSheets", [google_sheets])

    @staticmethod
    def get_google_slides():
        google_slides = Package("GoogleSlides", "com.google.android.apps.docs.editors.slides", Statics.is_system_app)
        return AppSet("GoogleSlides", [google_slides])

    @staticmethod
    def get_google_duo():
        google_duo = Package("GoogleDuo", "com.google.android.apps.tachyon", Statics.is_system_app)
        return AppSet("GoogleDuo", [google_duo])

    @staticmethod
    def get_device_personalization_services():
        device_personalization_services = Package("MatchmakerPrebuiltPixel4", "com.google.android.as",
                                                  Statics.is_priv_app, "DevicePersonalizationServices")
        gapps_list = []
        device_personalization_services.delete("DevicePersonalizationPrebuiltPixel4")
        gapps_list.append(device_personalization_services)
        return AppSet("DevicePersonalizationServices", gapps_list)

    @staticmethod
    def get_google_fi():
        google_fi_set = AppSet("GoogleFi")
        google_fi = Package("Tycho", "com.google.android.apps.tycho", Statics.is_system_app)
        google_fi_set.add_package(google_fi)
        gcs = Package("GCS", "com.google.android.apps.gcs", Statics.is_priv_app)
        google_fi_set.add_package(gcs)
        return google_fi_set

    @staticmethod
    def get_pixel_launcher(android_version):
        pixel_launcher = Package("NexusLauncherPrebuilt", "com.google.android.apps.nexuslauncher",
                                 Statics.is_priv_app, "PixelLauncher",
                                 partition=Statics.get_partition(android_version, "system_ext"))
        if float(android_version) >= 12.1:
            pixel_launcher_overlay = Overlay(pixel_launcher.package_title, "com.nikgapps.overlay.pixellauncher",
                                             android_version, Library.get_pixel_launcher_resources())
            pixel_launcher.add_overlay(pixel_launcher_overlay)
        pixel_launcher.priv_app_permissions.append("android.permission.PACKAGE_USAGE_STATS")
        pixel_launcher.delete("TrebuchetQuickStep")
        pixel_launcher.delete("Launcher3QuickStep")
        pixel_launcher.delete("ArrowLauncher")
        pixel_launcher.delete("Lawnchair")
        pixel_launcher.delete_overlay("Lawnchair")
        device_personalization_services = Package("MatchmakerPrebuiltPixel4", "com.google.android.as",
                                                  Statics.is_priv_app, "DevicePersonalizationServices")
        if float(android_version) >= 12.1:
            device_personalization_services_overlay = Overlay(device_personalization_services.package_title,
                                                              "com.nikgapps.overlay.ais", android_version,
                                                              Library.get_devices_personalization_services_resources())
            device_personalization_services.add_overlay(device_personalization_services_overlay)
        gapps_list = [pixel_launcher]
        if float(android_version) >= 9:
            device_personalization_services.delete("DevicePersonalizationPrebuiltPixel4")
            gapps_list.append(device_personalization_services)
        if float(android_version) >= 11:
            quick_access_wallet = Package("QuickAccessWallet", "com.android.systemui.plugin.globalactions.wallet",
                                          Statics.is_priv_app)
            quick_access_wallet.delete("QuickAccessWallet")
            gapps_list.append(quick_access_wallet)
        google_wallpaper = Package("WallpaperPickerGooglePrebuilt", "com.google.android.apps.wallpaper",
                                   Statics.is_priv_app, "GoogleWallpaper",
                                   partition=Statics.get_partition(android_version, "system_ext"))
        gapps_list.append(google_wallpaper)
        if float(android_version) >= 12:
            settings_services = Package("SettingsIntelligenceGooglePrebuilt",
                                        "com.google.android.settings.intelligence",
                                        Statics.is_priv_app, "SettingsServices")
            if float(android_version) >= 12.1:
                settings_services_overlay = Overlay(settings_services.package_title,
                                                    "com.nikgapps.overlay.settingsintelligence", android_version,
                                                    Library.get_settings_services_resources(android_version))
                settings_services.add_overlay(settings_services_overlay)
            device_intelligence_network_prebuilt = Package("DeviceIntelligenceNetworkPrebuilt",
                                                           "com.google.android.as.oss",
                                                           Statics.is_priv_app, "PrivateComputeServices")
            gapps_list.append(settings_services)
            gapps_list.append(device_intelligence_network_prebuilt)
        if float(android_version) >= 13:
            pixel_themes = Package("PixelThemes", "com.google.android.apps.customization.pixel", Statics.is_system_app)
            gapps_list.append(pixel_themes)
            emoji_wallpaper = Package("WallpaperEmojiPrebuilt", "com.google.android.apps.emojiwallpaper",
                                      Statics.is_system_app, "EmojiWallpaper")
            gapps_list.append(emoji_wallpaper)
            if float(android_version) >= 14:
                cinematic_effect = Package("WallpaperEffect", "com.google.android.wallpaper.effects",
                                           Statics.is_priv_app, "CinematicEffect")
                cinematic_effect_overlay = Overlay(cinematic_effect.package_title,
                                                   "com.nikgapps.overlay.cinematiceffect", android_version,
                                                   Library.get_cinematic_effect_resources())
                cinematic_effect.add_overlay(cinematic_effect_overlay)
                gapps_list.append(cinematic_effect)
            if float(android_version) >= 14:
                pixel_weather = Package("WeatherPixelPrebuilt", "com.google.android.apps.weather", Statics.is_priv_app,
                                        "PixelWeather")
                gapps_list.append(pixel_weather)
        return AppSet("PixelSpecifics", gapps_list)

    @staticmethod
    def get_google_play_books():
        google_play_books = Package("Books", "com.google.android.apps.books", Statics.is_system_app)
        return AppSet("Books", [google_play_books])

    @staticmethod
    def get_google_wallpaper(android_version):
        google_wallpaper = Package("WallpaperPickerGooglePrebuilt", "com.google.android.apps.wallpaper",
                                   Statics.is_priv_app, "GoogleWallpaper",
                                   partition=Statics.get_partition(android_version, "system_ext"))
        return AppSet("GoogleWallpaper", [google_wallpaper])

    @staticmethod
    def get_youtube_music(android_version):
        youtube_music = Package("YouTubeMusicPrebuilt", "com.google.android.apps.youtube.music",
                                Statics.is_system_app,
                                "YouTubeMusic")
        if float(android_version) >= 12.1:
            youtube_music_overlay = Overlay(youtube_music.package_title, "com.nikgapps.overlay.youtubemusic",
                                            android_version, Library.get_youtube_music_resources())
            youtube_music.add_overlay(youtube_music_overlay)
        youtube_music.delete("SnapdragonMusic")
        youtube_music.delete("GooglePlayMusic")
        youtube_music.delete("Eleven")
        youtube_music.delete("CrDroidMusic")
        return AppSet("YouTubeMusic", [youtube_music])

    @staticmethod
    def get_mixplorer():
        mixplorer_silver = Package("MixPlorerSilver", "com.mixplorer.silver", Statics.is_system_app,
                                   "MixPlorerSilver")
        mixplorer_silver.delete("MixPlorer")
        return AppSet("MixPlorerSilver", [mixplorer_silver])

    @staticmethod
    def get_adaway():
        adaway = Package("AdAway", "org.adaway", Statics.is_system_app)
        return AppSet("AdAway", [adaway])

    @staticmethod
    def get_lawnchair():
        lawnchair = Package("Lawnchair", "app.lawnchair", Statics.is_system_app)
        lawnchair.delete_overlay("PixelLauncher")
        lawnchair.delete("NexusLauncherPrebuilt")
        lawnchair.delete("NexusLauncherRelease")
        return AppSet("Lawnchair", [lawnchair])

    @staticmethod
    def get_pixel_live_wallpapers(android_version):
        pixel_live_wallpaper_set = AppSet("PixelLiveWallpapers")
        if float(android_version) == 13:
            pixel_live_wallpaper = Package("PixelLiveWallpaperPrebuilt", "com.google.pixel.livewallpaper",
                                           Statics.is_priv_app, "PixelLiveWallpaper")
            pixel_live_wallpaper_set.add_package(pixel_live_wallpaper)
            pixel_wallpapers_2022 = Package("PixelWallpapers2022", "com.google.android.apps.wallpaper.pixel",
                                            Statics.is_system_app)
            pixel_live_wallpaper_set.add_package(pixel_wallpapers_2022)
        return pixel_live_wallpaper_set

    @staticmethod
    def get_poke_pix_live_wallpapers():
        wallpapers_breel_2019 = Package("WallpapersBReel2019", "com.breel.wallpapers19", Statics.is_system_app)
        wallpapers_breel_2020a = Package("WallpapersBReel2020a", "com.breel.wallpapers20a", Statics.is_system_app)
        pixel_live_wallpaper = Package("PixelLiveWallpaperPrebuilt", "com.google.pixel.livewallpaper",
                                       Statics.is_priv_app, "PixelLiveWallpaper")
        wallpapers_breel_2020 = Package("WallpapersBReel2020", "com.breel.wallpapers20", Statics.is_system_app)
        pixel_live_wallpaper_set = AppSet("PokePixLiveWallpapers")
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2019)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020a)
        pixel_live_wallpaper_set.add_package(pixel_live_wallpaper)
        pixel_live_wallpaper_set.add_package(wallpapers_breel_2020)
        return pixel_live_wallpaper_set

    @staticmethod
    def get_youtube():
        youtube = Package("YouTube", "com.google.android.youtube", Statics.is_system_app)
        return AppSet("YouTube", [youtube])

    @staticmethod
    def get_pixel_setup_wizard(android_version):
        setup_wizard = Package("SetupWizardPrebuilt", "com.google.android.setupwizard", Statics.is_priv_app,
                               "SetupWizard")
        setup_wizard.delete("Provision")
        setup_wizard.additional_installer_script = """
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
   set_prop "ro.setupwizard.setupwizard.feature.show_support_link_in_deferred_setup" "false" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.enable_wifi_tracker" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.day_night_mode_enabled" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.portal_notification" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.lifecycle_refactoring" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
   set_prop "setupwizard.feature.notification_refactoring" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
                """
        google_restore = Package("GoogleRestore", "com.google.android.apps.restore", Statics.is_priv_app)
        pixel_setup_wizard_overlay = Package("PixelSetupWizardOverlay", "com.google.android.pixel.setupwizard.overlay",
                                             Statics.is_system_app)
        pixel_setup_wizard_aod_overlay = Package("PixelSetupWizardAodOverlay",
                                                 "com.google.android.pixel.setupwizard.overlay.aod",
                                                 Statics.is_system_app)
        pixel_setup_wizard = Package("PixelSetupWizard", "com.google.android.pixel.setupwizard", Statics.is_priv_app,
                                     partition=Statics.get_partition(android_version, "system_ext"))
        pixel_setup_wizard.delete("LineageSetupWizard")
        android_migrate_prebuilt = Package("AndroidMigratePrebuilt", "com.google.android.apps.pixelmigrate",
                                           Statics.is_priv_app)

        setup_wizard_set = AppSet("PixelSetupWizard")
        setup_wizard_set.add_package(setup_wizard)
        setup_wizard_set.add_package(google_restore)
        if float(android_version) >= 10:
            google_one_time_initializer = Package("GoogleOneTimeInitializer", "com.google.android.onetimeinitializer",
                                                  Statics.is_priv_app,
                                                  partition=Statics.get_partition(android_version, "system_ext"))
            setup_wizard_set.add_package(google_one_time_initializer)
        if float(android_version) == 10:
            setup_wizard_set.add_package(pixel_setup_wizard_overlay)
            setup_wizard_set.add_package(pixel_setup_wizard_aod_overlay)
        if float(android_version) >= 10:
            setup_wizard_set.add_package(pixel_setup_wizard)
            if float(android_version) < 12:
                setup_wizard_set.add_package(android_migrate_prebuilt)
        return setup_wizard_set

    @staticmethod
    def get_documents_ui():
        documents_ui = Package("DocumentsUI", "com.android.documentsui", Statics.is_priv_app)
        return AppSet("DocumentsUI", [documents_ui])
