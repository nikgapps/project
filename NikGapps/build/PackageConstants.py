class PackageConstants:

    @staticmethod
    def get_package_clean_flash_rule(package_name):
        package_clean_flash_packages = ["com.google.android.googlequicksearchbox",
                                        "com.google.android.inputmethod.latin",
                                        "com.google.android.deskclock",
                                        "com.google.android.apps.googleassistant",
                                        "com.google.android.soundpicker",
                                        "com.google.android.projection.gearhead"]
        return package_name in package_clean_flash_packages

    @staticmethod
    def get_package_deletes(package_name):
        package_deletes = {
            "com.google.android.gms": ["PrebuiltGmsCoreQt", "PrebuiltGmsCoreRvc", "GmsCore"],
            "com.google.android.dialer": ["Dialer"],
            "com.google.android.contacts": ["Contacts"],
            "com.google.android.tts": ["PicoTts"],
            "com.google.android.inputmethod.latin": ["LatinIME"],
            "com.google.android.calendar": ["Calendar", "Etar", "SimpleCalendar"],
            "com.google.android.apps.messaging": ["RevengeMessages", "messaging", "Messaging", "QKSMS", "Mms"],
            "com.google.android.apps.photos": ["Gallery", "SimpleGallery", "Gallery2", "MotGallery", "MediaShortcuts",
                                               "SimpleGallery", "FineOSGallery", "GalleryX", "MiuiGallery",
                                               "SnapdragonGallery", "DotGallery", "Glimpse"],
            "com.google.android.keep": ["Notepad"],
            "com.google.android.apps.recorder": ["Recorder", "QtiSoundRecorder"],
            "com.google.android.gm": ["Email", "PrebuiltEmailGoogle"],
            "com.google.android.apps.wallpaper": ["Wallpapers", "ThemePicker"],
            "com.android.chrome": ["Bolt", "Browser", "Browser2", "BrowserIntl", "BrowserProviderProxy", "Chromium",
                                   "DuckDuckGo", "Fluxion", "Gello", "Jelly", "PA_Browser", "PABrowser", "YuBrowser",
                                   "BLUOpera", "BLUOperaPreinstall", "ViaBrowser", "Duckduckgo"],
            "com.google.android.youtube.music": ["SnapdragonMusic", "GooglePlayMusic", "Eleven", "CrDroidMusic"],
            "com.google.android.setupwizard": ["Provision", "SetupWizard", "LineageSetupWizard"],
            "com.google.android.pixel.setupwizard": ["Provision", "SetupWizard", "LineageSetupWizard"],
            "com.google.android.calculator": ["ExactCalculator", "MotoCalculator", "RevengeOSCalculator"],
            "com.google.android.apps.maps": ["Maps"],
            "com.google.android.apps.turbo": ["TurboPrebuilt"],
            "com.google.android.soundpicker": ["SoundPicker"],
            "com.google.android.storagemanager": ["StorageManager"],
            "com.google.android.documentsui": ["DocumentsUI"],
            "com.google.android.webview": ["webview"],
            "com.google.android.apps.restore": ["Seedvault"],
            "com.google.android.deskclock": ["DeskClock"],
            "org.lineageos.snap": ["GoogleCameraGo", "ScreenRecorder"],
            "com.google.android.as": ["DevicePersonalizationPrebuiltPixel4"],
            "com.google.android.apps.nexuslauncher": ["TrebuchetQuickStep", "Launcher3QuickStep", "ArrowLauncher",
                                                      "Lawnchair"],
            "com.android.systemui.plugin.globalactions.wallet": ["QuickAccessWallet"],
            "com.google.android.apps.youtube.music": ["SnapdragonMusic", "GooglePlayMusic", "Eleven", "CrDroidMusic"],
            "com.mixplorer.silver": ["MixPlorer"],
            "app.lawnchair": ["Lawnchair"]
        }
        return package_deletes.get(package_name, [])

    @staticmethod
    def get_package_script(package_name):
        package_scripts = {
            "ExtraFiles": """   script_text="<permissions>
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
               fi
               script_text="<permissions>
                <library name=\\"com.google.android.maps\\"
                        file=\\"$install_partition/framework/com.google.android.maps.jar\\" />
            </permissions>"
               echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.maps.xml
               set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.maps.xml"
               update_prop "$install_partition/etc/permissions/com.google.android.maps.xml" "install" "$propFilePath" "$package_title"
               if [ -f "$install_partition/etc/permissions/com.google.android.maps.xml" ]; then
                 addToLog "- $install_partition/etc/permissions/com.google.android.maps.xml Successfully Written!" "$package_title"
               fi
               script_text="<permissions>
            <library name=\\"com.google.widevine.software.drm\\"
            file=\\"/system/product/framework/com.google.widevine.software.drm.jar\\"/>
            </permissions>"
               echo -e "$script_text" > $install_partition/etc/permissions/com.google.widevine.software.drm.xml
               set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.widevine.software.drm.xml"
               update_prop "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" "install" "$propFilePath" "$package_title"
               if [ -f "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" ]; then
                 addToLog "- $install_partition/etc/permissions/com.google.widevine.software.drm.xml Successfully Written!" "$package_title"
               fi
               script_text="<permissions>
            <library name=\\"com.google.android.media.effects\\"
            file=\\"$install_partition/framework/com.google.android.media.effects.jar\\" />

            </permissions>"
               echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.media.effects.xml
               set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.media.effects.xml"
               update_prop "$install_partition/etc/permissions/com.google.android.media.effects.xml" "install" "$propFilePath" "$package_title"
               if [ -f "$install_partition/etc/permissions/com.google.android.media.effects.xml" ]; then
                 addToLog "- $install_partition/etc/permissions/com.google.android.media.effects.xml Successfully Written!" "$package_title"
               fi
        """,
            "ExtraFilesGo": """   script_text="<permissions>
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
       fi
       script_text="<permissions>
        <library name=\\"com.google.android.maps\\"
                file=\\"$install_partition/framework/com.google.android.maps.jar\\" />
    </permissions>"
       echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.maps.xml
       set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.maps.xml"
       update_prop "$install_partition/etc/permissions/com.google.android.maps.xml" "install" "$propFilePath" "$package_title"
       if [ -f "$install_partition/etc/permissions/com.google.android.maps.xml" ]; then
         addToLog "- $install_partition/etc/permissions/com.google.android.maps.xml Successfully Written!" "$package_title"
       fi
       script_text="<permissions>
    <library name=\\"com.google.widevine.software.drm\\"
    file=\\"/system/product/framework/com.google.widevine.software.drm.jar\\"/>
    </permissions>"
       echo -e "$script_text" > $install_partition/etc/permissions/com.google.widevine.software.drm.xml
       set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.widevine.software.drm.xml"
       update_prop "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" "install" "$propFilePath" "$package_title"
       if [ -f "$install_partition/etc/permissions/com.google.widevine.software.drm.xml" ]; then
         addToLog "- $install_partition/etc/permissions/com.google.widevine.software.drm.xml Successfully Written!" "$package_title"
       fi
       script_text="<permissions>
    <library name=\\"com.google.android.media.effects\\"
    file=\\"$install_partition/framework/com.google.android.media.effects.jar\\" />

    </permissions>"
       echo -e "$script_text" > $install_partition/etc/permissions/com.google.android.media.effects.xml
       set_perm 0 0 0644 "$install_partition/etc/permissions/com.google.android.media.effects.xml"
       update_prop "$install_partition/etc/permissions/com.google.android.media.effects.xml" "install" "$propFilePath" "$package_title"
       if [ -f "$install_partition/etc/permissions/com.google.android.media.effects.xml" ]; then
         addToLog "- $install_partition/etc/permissions/com.google.android.media.effects.xml Successfully Written!" "$package_title"
       fi
        """,
            "GmsCore": """
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
            "SetupWizard": """
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
            "Velvet": """
       set_prop "ro.opa.eligible_device" "true" "$product/etc/build.prop" "$propFilePath" "$package_title"
        """,
            "GBoard": """
       set_prop "ro.com.google.ime.theme_id" "5" "$product/etc/build.prop" "$propFilePath" "$package_title"
       set_prop "ro.com.google.ime.kb_pad_port_b" "8" "$product/etc/build.prop" "$propFilePath" "$package_title"
       set_prop "ro.com.google.ime.height_ratio" "1.025" "$product/etc/build.prop" "$propFilePath" "$package_title"
       set_prop "ro.com.google.ime.system_lm_dir" "$install_partition/usr/share/ime/google/d3_lms" "$product/etc/build.prop" "$propFilePath" "$package_title"
        """
        }
        return package_scripts.get(package_name, None)