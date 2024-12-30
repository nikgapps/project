from NikGapps.helper.overlay.Bool import Bool
from NikGapps.helper.overlay.Resources import Resources
from NikGapps.helper.overlay.String import String
from NikGapps.helper.overlay.StringArray import StringArray


class Library:

    @staticmethod
    def get_google_dialer_resources():
        r = Resources()
        r.add(String('config_defaultDialer', 'com.google.android.dialer',
                     comment='The name of the package that will hold the dialer role by default.'))
        r.add(String('dialer_default_class', 'com.google.android.dialer.extensions.GoogleDialtactsActivity',
                     comment='Class name for the default main Dialer activity'))
        r.add(String('incall_default_class', 'com.android.incallui.InCallServiceImpl'))
        r.add(String('config_defaultCallRedirection', 'com.google.android.dialer'))
        r.add(String('config_defaultCallScreening', 'com.google.android.dialer'))
        r.add(Bool('grant_location_permission_enabled', True,
                   comment='Determines if the granting of temporary location permission to the default dialer '
                           'during an emergency call should be allowed.'))
        r.add(Bool('call_recording_enabled', True))
        r.add(StringArray('config_globallyDisabledComponents', [
            'com.google.android.dialer/com.android.dialer.rtt.settings.impl.gateway.RttSettingsDeepLink']))
        return r

    @staticmethod
    def get_android_auto_resources():
        r = Resources()
        r.add(String("config_systemAutomotiveProjection", "com.google.android.projection.gearhead",
                     comment="The names of the packages that will hold the system automotive projection role."))
        return r

    @staticmethod
    def get_google_contacts_resources():
        r = Resources()
        r.add(String('config_systemContacts', 'com.google.android.contacts',
                     comment='The name of the package that will hold the contacts role by default.'))
        return r

    @staticmethod
    def get_digital_wellbeing_resources():
        r = Resources()
        r.add(String('config_systemWellbeing', 'com.google.android.apps.wellbeing',
                     comment='The name of the package that will hold the wellbeing role by default.'))
        r.add(String('config_defaultWellbeingPackage', 'com.google.android.apps.wellbeing',
                     comment='The package name for the default wellbeing application.'))
        r.add(String('config_defaultDndAccessPackages', 'com.google.android.gms:com.google.android.apps.wellbeing',
                     comment='Colon separated list of package names that should be granted DND access.'))
        r.add(StringArray('config_packagesExemptFromSuspension', ['com.google.android.apps.wellbeing']))
        r.add(StringArray('config_quickSettingsAutoAdd', ['wind_down_first_time_setup:custom(com.google.android.apps.wellbeing/.screen.ui.GrayscaleTileService)',
                                                          'focus_mode_first_time_setup:custom(com.google.android.apps.wellbeing/.focusmode.quicksettings.FocusModeTileService)']))
        return r

    @staticmethod
    def get_flipendo_resources():
        r = Resources()
        r.add(String('config_powerSaveModeChangedListenerPackage', 'com.google.android.flipendo'))
        return r

    @staticmethod
    def get_gms_core_resources():
        r = Resources()
        r.add(String('config_defaultDndAccessPackages', 'com.google.android.gms:com.google.android.apps.wellbeing',
                     comment='Colon separated list of package names that should be granted DND access.'))
        r.add(String('config_defaultSupervisionProfileOwnerComponent',
                     'com.google.android.gms/.kids.account.receiver.ProfileOwnerReceiver'))
        r.add(String('config_systemSupervision', 'com.google.android.gms.supervision'))
        r.add(String('def_backup_transport', 'com.google.android.gms/.backup.BackupTransportService'))
        r.add(String('metadata_sync_pacakge', 'com.google.android.gms'))
        r.add(String('config_defaultAutofillService', 'com.google.android.gms/.autofill.service.AutofillService'))
        r.add(String('config_defaultNearbySharingComponent',
                     'com.google.android.gms/com.google.android.gms.nearby.sharing.ShareSheetActivity'))
        r.add(String('config_defaultNearbyFastPairSettingsDevicesComponent',
                     'com.google.android.gms/com.google.android.gms.nearby.discovery.devices.SavedDevicesSettingsActivity'))
        r.add(String('config_defaultNetworkRecommendationProviderPackage', 'com.google.android.gms'))
        r.add(String('config_persistentDataPackageName', 'com.google.android.gms'))
        r.add(String('config_systemCompanionDeviceProvider', 'com.google.android.gms'))
        r.add(String('config_appsAuthorizedForSharedAccounts', ';com.android.vending;com.android.settings;'))
        r.add(String('config_deviceConfiguratorPackageName', 'com.google.android.gms'))
        r.add(String('config_systemGameService', 'com.google.android.gms'))
        r.add(String('config_systemActivityRecognizer', 'com.google.android.gms'))
        r.add(String('config_devicePolicyManagementUpdater', 'com.google.android.gms'))
        r.add(String('platform_number_verification_package', 'com.google.android.gms'))
        r.add(String('config_defaultQrCodeComponent',
                     'com.google.android.gms/.mlkit.barcode.ui.PlatformBarcodeScanningActivityProxy'))
        r.add(String('config_defaultCredentialManagerHybridService', 'com.google.android.gms/.auth.api.credentials.credman.service.RemoteService'))
        r.add(String('config_remoteCopyPackage', 'com.google.android.gms/.nearby.sharing.RemoteCopyShareSheetActivity'))
        r.add(String('config_systemCallStreaming', 'com.google.android.gms'))
        r.add(String('config_oemCredentialManagerDialogComponent', 'com.google.android.gms/.identitycredentials.ui.CredentialChooserActivity'))
        r.add(Bool('config_enableAutoPowerModes', True))
        r.add(Bool('config_enableNetworkLocationOverlay', True))
        r.add(Bool('config_enableFusedLocationOverlay', True))
        r.add(Bool('config_enableGeocoderOverlay', True))
        r.add(Bool('config_enableGeofenceOverlay', True))
        r.add(Bool('vvm3_enabled', True))
        r.add(StringArray('config_priorityOnlyDndExemptPackages',
                          ['com.android.dialer', 'com.google.android.dialer', 'com.android.server.telecom', 'android',
                           'com.android.systemui']))
        r.add(StringArray('config_accessibility_allowed_install_source', ['com.android.vending']))
        r.add(StringArray('config_forceQueryablePackages',
                          ['com.android.settings', 'com.android.providers.settings', 'com.android.vending',
                           'com.google.android.gms']))
        r.add(StringArray('config_integrityRuleProviderPackages', ['com.android.vending', 'com.google.android.gms']))
        r.add(StringArray('config_disabledUntilUsedPreinstalledImes', ['com.google.android.inputmethod.latin']))
        r.add(StringArray('config_locationProviderPackageNames',
                          ['com.google.android.gms', 'com.android.location.fused']))
        r.add(StringArray('config_ephemeralResolverPackage', ['com.google.android.gms']))
        r.add(StringArray('config_globallyDisabledComponents', [
            'com.android.vending/com.google.android.finsky.systemupdate.SystemUpdateSettingsContentProvider',
            'com.android.vending/com.google.android.finsky.systemupdateactivity.SettingsSecurityEntryPoint',
            'com.android.vending/com.google.android.finsky.systemupdateactivity.SystemUpdateActivity',
            'com.google.android.gms/com.google.android.gms.update.phone.PopupDialog',
            'com.google.android.gms/com.google.android.gms.update.OtaSuggestionSummaryProvider',
            'com.google.android.gms/com.google.android.gms.update.SystemUpdateActivity',
            'com.google.android.gms/com.google.android.gms.update.SystemUpdateGcmTaskService',
            'com.google.android.gms/com.google.android.gms.update.SystemUpdateService',
            'com.google.android.gms/com.google.android.gms.update.SystemUpdateService.ActiveReceiver',
            'com.google.android.gms/com.google.android.gms.update.SystemUpdateService.Receiver',
            'com.google.android.gms/com.google.android.gms.update.SystemUpdateService.SecretCodeReceiver',
            'com.google.android.gms/com.google.android.gms.chimera.GmsIntentOperationService$GmsExternalReceiver']))
        return r

    @staticmethod
    def get_google_location_history_resources():
        r = Resources()
        r.add(StringArray('config_locationProviderPackageNames',
                          ['com.google.android.gms', 'com.android.location.fused',
                           'com.google.android.gms.location.history']))
        return r

    @staticmethod
    def get_google_messages_resources():
        r = Resources()
        r.add(String('config_defaultSms', 'com.google.android.apps.messaging'))
        return r

    @staticmethod
    def get_google_photos_resources():
        r = Resources()
        r.add(String('config_systemGallery', 'com.google.android.apps.photos'))
        r.add(String('config_defaultGallery', 'com.google.android.apps.photos'))
        return r

    @staticmethod
    def get_google_talkback_resources():
        r = Resources()
        r.add(String('config_defaultAccessibilityService', 'com.google.android.marvin.talkback/.TalkBackService'))
        r.add(StringArray('config_preinstalled_screen_reader_services',
                          ['com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService',
                           'com.google.android.marvin.talkback/com.google.android.accessibility.selecttospeak.SelectToSpeakService']))
        r.add(StringArray('config_preinstalled_interaction_control_services',
                          ['com.google.android.marvin.talkback/com.android.switchaccess.SwitchAccessService',
                           'com.google.android.marvin.talkback/com.google.android.accessibility.accessibilitymenu.AccessibilityMenuService']))
        return r

    @staticmethod
    def get_google_tts_resources():
        r = Resources()
        r.add(String('config_systemSpeechRecognizer', 'com.google.android.tts'))
        return r

    @staticmethod
    def get_pixel_launcher_resources():
        r = Resources()
        r.add(String('config_recentsComponentName',
                     'com.google.android.apps.nexuslauncher/com.android.quickstep.RecentsActivity'))
        r.add(String('config_secondaryHomePackage', 'com.google.android.apps.nexuslauncher'))
        r.add(String('exit_to_action_in_initial_setup',
                     'com.google.android.apps.nexuslauncher/com.android.quickstep.action.GESTURE_ONBOARDING_ALL_SET'))
        r.add(Bool('config_swipe_up_gesture_setting_available', True))
        r.add(Bool('config_custom_swipe_up_gesture_setting_available', True))
        r.add(StringArray('configs_base',
                          ['launcher/enable_one_search=true', 'launcher/ENABLE_LOCAL_RECOMMENDED_WIDGETS_FILTER=true',
                           'launcher/ENABLE_SMARTSPACE_ENHANCED=true',
                           'launcher/ENABLE_WIDGETS_PICKER_AIAI_SEARCH=true']))
        return r

    @staticmethod
    def get_velvet_resources():
        r = Resources()
        r.add(String('config_defaultAssistant', 'com.google.android.googlequicksearchbox'))
        r.add(String('config_defaultContextualSearchPackageName', 'com.google.android.googlequicksearchbox'))
        r.add(Bool('config_allowDisablingAssistDisclosure', True))
        return r

    @staticmethod
    def get_youtube_music_resources():
        r = Resources()
        r.add(String('config_defaultMusic', 'com.google.android.apps.youtube.music'))
        return r

    @staticmethod
    def get_template():
        return Resources()

    @staticmethod
    def get_device_health_services_resources():
        r = Resources()
        r.add(String('battery_suggestion_summary', 'Turn on Adaptive Battery'))
        r.add(String('smart_battery_manager_title', 'Adaptive Battery'))
        r.add(String('smart_battery_footer', 'When Battery Manager detects that apps are draining battery, you\u2019ll have the option to restrict these apps. Restricted apps may not work properly and notifications may be delayed.'))
        r.add(String('smart_battery_title', 'Use Adaptive Battery'))
        r.add(String('battery_tip_smart_battery_summary', 'Turn on Adaptive Battery'))
        return r

    @staticmethod
    def get_devices_personalization_services_resources():
        r = Resources()
        r.add(String('config_defaultAmbientContextConsentComponent',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.ambientcontext.ui.ConsentActivity'))
        r.add(String('config_defaultWallpaperEffectsGenerationService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.wallpapereffects.AiAiWallpaperEffectsGenerationService'))
        r.add(String('config_defaultAmbientContextDetectionService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAmbientContextDetectionService'))
        r.add(String('config_defaultAppPredictionService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService'))
        r.add(String('config_defaultAttentionService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.attention.service.AiAiAttentionService'))
        r.add(String('config_defaultSystemCaptionsManagerService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService'))
        r.add(String('config_defaultAugmentedAutofillService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService'))
        r.add(String('config_defaultContentCaptureService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService'))
        r.add(String('config_defaultListenerAccessPackages',
                     'com.android.launcher3:com.google.android.apps.nexuslauncher:com.google.android.apps.restore:com.google.android.setupwizard:com.google.android.apps.pixelmigrate:com.google.android.as:com.google.android.projection.gearhead'))
        r.add(String('config_defaultContentSuggestionsService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService'))
        r.add(String('config_defaultRotationResolverService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiRotationResolverService'))
        r.add(String('config_defaultSystemCaptionsService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.captions.CaptionsService'))
        r.add(String('config_systemAmbientAudioIntelligence', 'com.google.android.as'))
        r.add(String('config_systemAudioIntelligence', 'com.google.android.as'))
        r.add(String('config_systemNotificationIntelligence', 'com.google.android.as'))
        r.add(String('config_defaultSearchUiService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService'))
        r.add(String('config_systemTextIntelligence', 'com.google.android.as'))
        r.add(String('config_systemUiIntelligence', 'com.google.android.as'))
        r.add(String('config_systemVisualIntelligence', 'com.google.android.as'))
        r.add(String('config_defaultSmartspaceService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService'))
        r.add(String('config_defaultTranslationService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiTranslationService'))
        r.add(String('config_defaultAssistantAccessComponent',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService'))
        r.add(String('config_defaultOnDeviceSpeechRecognitionService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSpeechRecognitionService'))
        r.add(Bool('config_adaptive_sleep_available', True))
        r.add(Bool('config_systemCaptionsServiceCallsEnabled', True))
        r.add(StringArray('configs_base', ['device_personalization_services/Captions__allow_box_x_axis_movement=true',
                                           'device_personalization_services/Captions__allow_use_public_speech_recognition=true',
                                           'device_personalization_services/Captions__allow_voip_call_without_audio_recording=true',
                                           'device_personalization_services/Captions__available_for_download=en-US;en-GB;en-CA;en-IE;en-AU;en-SG;en-IN;fr-FR;fr-CA;fr-BE;fr-CH;it-IT;it-CH;de-DE;de-AT;de-BE;de-CH;ja-JP;es-ES;es-US;cmn-Hant-TW;hi-IN;pt-BR;tr-TR;pl-PL;cmn-Hans-CN;ko-KR;ru-RU;vi-VN',
                                           'device_personalization_services/Captions__disable_prod=false',
                                           'device_personalization_services/Captions__enable_activation_boost=true',
                                           'device_personalization_services/Captions__enable_adaptive_box_width=true',
                                           'device_personalization_services/Captions__enable_augmented_modality=true',
                                           'device_personalization_services/Captions__enable_augmented_modality_input=true',
                                           'device_personalization_services/Captions__enable_augmented_modality_language_detection=true',
                                           'device_personalization_services/Captions__enable_augmented_music=true',
                                           'device_personalization_services/Captions__enable_drag_and_double_tap_to_resize=true',
                                           'device_personalization_services/Captions__enable_ec_integration=false',
                                           'device_personalization_services/Captions__enable_language_detection=true',
                                           'device_personalization_services/Captions__enable_new_model_version_advanced_2023=true',
                                           'device_personalization_services/Captions__enable_one_caption_experiment=false',
                                           'device_personalization_services/Captions__enable_punctuations=true',
                                           'device_personalization_services/Captions__enable_setting_page=false',
                                           'device_personalization_services/Captions__enable_survey=false',
                                           'device_personalization_services/Captions__enable_text_transform=true',
                                           'device_personalization_services/Captions__enable_westworld_logging=false',
                                           'device_personalization_services/Captions__enable_zero_day=false',
                                           'device_personalization_services/Captions__manifest_url_template=https://storage.googleapis.com/captions/%{NAMESPACE}_%{VERSION}_manifest.json',
                                           'device_personalization_services/Captions__model_version_v1=20190613',
                                           'device_personalization_services/Captions__model_version_v1_2=20200112',
                                           'device_personalization_services/Captions__new_model_version=20210623',
                                           'device_personalization_services/Captions__new_model_version_advanced_2023=20230808',
                                           'device_personalization_services/Captions__speech_threshold=0.2',
                                           'device_personalization_services/Captions__support_lang_id_disabled_after_dismissals=true',
                                           'device_personalization_services/Captions__supported_languages=en-US;fr-FR;it-IT;de-DE;ja-JP;es-ES;cmn-Hant-TW;hi-IN;pt-BR;tr-TR;pl-PL;cmn-Hans-CN;ko-KR;ru-RU;vi-VN',
                                           'device_personalization_services/Captions__supported_languages_beta_quality=ja-JP;pt-BR;tr-TR;pl-PL;cmn-Hans-CN;ko-KR;ru-RU;vi-VN',
                                           'device_personalization_services/Captions__surface_sound_events=true',
                                           'device_personalization_services/Captions__text_transform_augmented_input=true',
                                           'device_personalization_services/Captions__visibility_playing_duration_millis=5000',
                                           'device_personalization_services/Captions__visibility_stopped_duration_millis=1500',
                                           'device_personalization_services/Echo__search_enable_all_fallback_results=true',
                                           'device_personalization_services/Echo__search_enable_allowlist=true',
                                           'device_personalization_services/Echo__search_enable_app_fetcher_v2=true',
                                           'device_personalization_services/Echo__search_enable_app_search_tips=true',
                                           'device_personalization_services/Echo__search_enable_app_token_indexing=false',
                                           'device_personalization_services/Echo__search_enable_app_usage_stats_ranking=true',
                                           'device_personalization_services/Echo__search_enable_application_header_type=true',
                                           'device_personalization_services/Echo__search_enable_apps=true',
                                           'device_personalization_services/Echo__search_enable_appsearch_tips_ranking_improvement=true',
                                           'device_personalization_services/Echo__search_enable_assistant_quick_phrases_settings=true',
                                           'device_personalization_services/Echo__search_enable_bc_smartspace_settings=true',
                                           'device_personalization_services/Echo__search_enable_bc_translate_settings=true',
                                           'device_personalization_services/Echo__search_enable_eventstore=true',
                                           'device_personalization_services/Echo__search_enable_everything_else_above_web=true',
                                           'device_personalization_services/Echo__search_enable_fetcher_optimization_using_result_types=true',
                                           'device_personalization_services/Echo__search_enable_filter_pending_jobs=true',
                                           'device_personalization_services/Echo__search_enable_mdp_play_results=true',
                                           'device_personalization_services/Echo__search_enable_play=true',
                                           'device_personalization_services/Echo__search_enable_play_alleyoop=true',
                                           'device_personalization_services/Echo__search_enable_scraping=true',
                                           'device_personalization_services/Echo__search_enable_search_in_app_icon=true',
                                           'device_personalization_services/Echo__search_enable_settings_corpus=true',
                                           'device_personalization_services/Echo__search_enable_shortcuts=true',
                                           'device_personalization_services/Echo__search_enable_static_shortcuts=true',
                                           'device_personalization_services/Echo__search_enable_superpacks_app_terms=true',
                                           'device_personalization_services/Echo__search_enable_superpacks_play_results=true',
                                           'device_personalization_services/Echo__search_enable_top_hit_row=true',
                                           'device_personalization_services/Echo__search_enable_widget_corpus=true',
                                           'device_personalization_services/Echo__search_play_enable_spell_correction=true',
                                           'device_personalization_services/Cell__enable_cell=true',
                                           'device_personalization_services/Cell__enable_smartspace_events=true',
                                           'device_personalization_services/EchoSmartspace__check_notification_visibility=true',
                                           'device_personalization_services/EchoSmartspace__doorbell_when_for_update_time=true',
                                           'device_personalization_services/EchoSmartspace__enable_add_contextual_feedback_button_on_long_press=false',
                                           'device_personalization_services/EchoSmartspace__enable_add_internal_feedback_button=true',
                                           'device_personalization_services/EchoSmartspace__enable_agsa_settings_read=true',
                                           'device_personalization_services/EchoSmartspace__enable_cross_feature_rank_dedup_twiddler=true',
                                           'device_personalization_services/EchoSmartspace__enable_dimensional_logging=true',
                                           'device_personalization_services/EchoSmartspace__enable_encode_subcard_into_smartspace_target_id=true',
                                           'device_personalization_services/EchoSmartspace__enable_flight_landing_smartspace_aiai=true',
                                           'device_personalization_services/EchoSmartspace__enable_hotel_smartspace_aiai=true',
                                           'device_personalization_services/EchoSmartspace__enable_media_recs_for_driving=true',
                                           'device_personalization_services/EchoSmartspace__enable_predictor_expiration=true',
                                           'device_personalization_services/EchoSmartspace__enable_ring_channels_regex=true',
                                           'device_personalization_services/EchoSmartspace__enable_ring_using_ui_template=true',
                                           'device_personalization_services/EchoSmartspace__enable_travel_features_type_merge=true',
                                           'device_personalization_services/EchoSmartspace__ring_lockscreen_delay_seconds=0',
                                           'device_personalization_services/EchoSmartspace__ring_on_aod_only=true',
                                           'device_personalization_services/EchoSmartspace__runtastic_check_pause_action=true',
                                           'device_personalization_services/EchoSmartspace__runtastic_is_ongoing_default_true=true',
                                           'device_personalization_services/EchoSmartspace__smartspace_enable_daily_forecast=true',
                                           'device_personalization_services/EchoSmartspace__smartspace_enable_timely_reminder=true',
                                           'device_personalization_services/EchoSmartspace__strava_check_stop_action=true',
                                           'device_personalization_services/Echo__smartspace_dedupe_fast_pair_notification=true',
                                           'device_personalization_services/Echo__smartspace_doorbell_aiai_loading_screen=false',
                                           'device_personalization_services/Echo__smartspace_doorbell_allowlist_packages=com.nest.android, com.google.android.apps.chromecast.app',
                                           'device_personalization_services/Echo__smartspace_doorbell_loading_screen_state=4',
                                           'device_personalization_services/Echo__smartspace_enable_async_icon=true',
                                           'device_personalization_services/Echo__smartspace_enable_battery_notification_parser=true',
                                           'device_personalization_services/Echo__smartspace_enable_bedtime_active_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_bedtime_reminder_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_bluetooth_metadata_parser=true',
                                           'device_personalization_services/Echo__smartspace_enable_cross_device_timer=true',
                                           'device_personalization_services/Echo__smartspace_enable_dark_launch_outlook_events=true',
                                           'device_personalization_services/Echo__smartspace_enable_doorbell=true',
                                           'device_personalization_services/Echo__smartspace_enable_doorbell_context_wrapper=true',
                                           'device_personalization_services/Echo__smartspace_enable_doorbell_extras=true',
                                           'device_personalization_services/Echo__smartspace_enable_dwb_bedtime_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_earthquake_alert_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_echo_settings=true',
                                           'device_personalization_services/Echo__smartspace_enable_echo_unified_settings=true',
                                           'device_personalization_services/Echo__smartspace_enable_eta_doordash=true',
                                           'device_personalization_services/Echo__smartspace_enable_eta_lyft=true',
                                           'device_personalization_services/Echo__smartspace_enable_food_delivery_eta=true',
                                           'device_personalization_services/Echo__smartspace_enable_grocery=true',
                                           'device_personalization_services/Echo__smartspace_enable_light_off_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_light_predictor=false',
                                           'device_personalization_services/Echo__smartspace_enable_media_wake_lock_acquire=true',
                                           'device_personalization_services/Echo__smartspace_enable_nap=true',
                                           'device_personalization_services/Echo__smartspace_enable_nudge=true',
                                           'device_personalization_services/Echo__smartspace_enable_outlook_events=true',
                                           'device_personalization_services/Echo__smartspace_enable_package_delivery=true',
                                           'device_personalization_services/Echo__smartspace_enable_paired_device_connections=true',
                                           'device_personalization_services/Echo__smartspace_enable_paired_device_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_ridesharing_eta=true',
                                           'device_personalization_services/Echo__smartspace_enable_safety_check_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_score_ranker=true',
                                           'device_personalization_services/Echo__smartspace_enable_sensitive_notification_twiddler=true',
                                           'device_personalization_services/Echo__smartspace_enable_step_predictor=true',
                                           'device_personalization_services/Echo__smartspace_enable_subcard_logging=true',
                                           'device_personalization_services/Echo__smartspace_gaia_twiddler=true',
                                           'device_personalization_services/Echo__smartspace_outlook_event_source_of_truth=TEXT_ONLY',
                                           'device_personalization_services/Echo__smartspace_package_delivery_card_delay_seconds=0',
                                           'device_personalization_services/Echo__smartspace_show_cross_device_timer_label=true',
                                           'device_personalization_services/Echo__smartspace_use_flashlight_action_chip=true',
                                           'device_personalization_services/Echo_smartspace__enable_flight_landing_smartspace_aiai=true',
                                           'device_personalization_services/Echo_smartspace__enable_hotel_smartspace_aiai=true',
                                           'device_personalization_services/Echo_smartspace__smartspace_enable_daily_forecast=true',
                                           'device_personalization_services/Echo_smartspace__smartspace_enable_timely_reminder=true',
                                           'device_personalization_services/Overview__enable_barcode_detection=false',
                                           'device_personalization_services/Overview__enable_image_search=false',
                                           'device_personalization_services/Overview__enable_image_selection=true',
                                           'device_personalization_services/Overview__enable_japanese_ocr=true',
                                           'device_personalization_services/Overview__enable_lens_r_overview_long_press=true',
                                           'device_personalization_services/Overview__enable_lens_r_overview_select_mode=true',
                                           'device_personalization_services/Overview__enable_lens_r_overview_translate_action=false',
                                           'device_personalization_services/Overview__enable_overview=true',
                                           'device_personalization_services/Overview__enable_pir_clearcut_logging=true',
                                           'device_personalization_services/Overview__enable_pir_westworld_logging=true',
                                           'device_personalization_services/Overview__enable_proactive_hints=false',
                                           'device_personalization_services/Overview__enable_superpacks_pir_protocol=true',
                                           'device_personalization_services/Overview__min_lens_agsa_app_version=301084649',
                                           'device_personalization_services/Translate__app_blocklist=com.google.android.talk',
                                           'device_personalization_services/Translate__blue_chip_translate_enabled=true',
                                           'device_personalization_services/Translate__characterset_lang_detection_enabled=true',
                                           'device_personalization_services/Translate__chat_translate_languages=de,en,es,fr,it,ja,hi,zh,ru,pl,pt,ko,th,tr,nl,zh_Hant,sv,da,vi,ar,fa,no,bn,fil',
                                           'device_personalization_services/Translate__copy_to_translate_enabled=true',
                                           'device_personalization_services/Translate__differentiate_simplified_and_traditional_chinese=true',
                                           'device_personalization_services/Translate__disable_translate_without_system_animation=false',
                                           'device_personalization_services/Translate__enable_chronicle_migration=true',
                                           'device_personalization_services/Translate__enable_default_langid_model=true',
                                           'device_personalization_services/Translate__enable_dictionary_langid_detection=true',
                                           'device_personalization_services/Translate__enable_opmv4_service=true',
                                           'device_personalization_services/Translate__enable_settings_backup_restore=false',
                                           'device_personalization_services/Translate__enable_setup_wizard_dialog_v2=false',
                                           'device_personalization_services/Translate__enable_spa_setting=false',
                                           'device_personalization_services/Translate__enable_translate_kit_api_migration=false',
                                           'device_personalization_services/Translate__interpreter_source_languages=de,en,ja,es,fr,it',
                                           'device_personalization_services/Translate__interpreter_target_languages=de,en,ja,es,fr,it',
                                           'device_personalization_services/Translate__replace_auto_translate_copied_text_enabled=true',
                                           'device_personalization_services/Translate__text_to_text_language_list=vi,ja,fa,ro,nl,mr,mt,ar,ms,it,eo,is,et,es,iw,zh,uk,af,id,ur,mk,cy,hi,el,be,pt,lt,hr,lv,hu,ht,te,de,bg,th,bn,tl,pl,tr,kn,sv,gl,ko,sw,cs,da,ta,gu,ka,sl,ca,sk,ga,sq,no,fi,ru,fr,en,zh_Hant,fil',
                                           'device_personalization_services/Translate__translation_service_enabled=true',
                                           'device_personalization_services/Translate__translator_expiration_enabled=true',
                                           'device_personalization_services/Translate__use_translate_kit_streaming_api=true',
                                           'device_personalization_services/SmartDictation__enable_alternatives_from_past_corrections=true',
                                           'device_personalization_services/SmartDictation__enable_alternatives_from_speech_hypotheses=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_commands=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_contact_fields=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_contacts=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_contacts_learned_from_past_corrections=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_interests_model=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_past_correction=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_past_corrections=true',
                                           'device_personalization_services/SmartDictation__enable_biasing_for_screen_context=true',
                                           'device_personalization_services/SmartDictation__enable_personalized_biasing_on_locked_device=false',
                                           'device_personalization_services/SmartDictation__enable_selection_filtering=true',
                                           'device_personalization_services/SmartDictation__enable_stronger_boost_for_generic_phrases_biasing=false',
                                           'device_personalization_services/SmartRecCompose__enable_aiai_tc_generator=true',
                                           'device_personalization_services/SmartRecCompose__enable_compose_action_filter=true',
                                           'device_personalization_services/SmartRecCompose__enable_compose_tc=true',
                                           'device_personalization_services/SmartRecCompose__enable_deep_clu_model=true',
                                           'device_personalization_services/SmartRecOverviewChips__enable_action_boost_generator=true',
                                           'device_personalization_services/SmartRecOverviewChips__enable_assistant_geller_data_index=false',
                                           'device_personalization_services/SmartRecOverviewChips__enable_matchmaker_generator=true',
                                           'device_personalization_services/SmartRecOverviewChips__enable_reflection_generator=true',
                                           'device_personalization_services/SmartRecOverviewChips__enable_settings_card_generator=true',
                                           'device_personalization_services/SmartRecOverviewChips__enable_smartrec_for_overview_chips=true',
                                           'device_personalization_services/SmartRecOverviewChips__nasa_superpacks_manifest_url=https://www.gstatic.com/nasa/apps/pack_enus_10062022/22100618/2/en-us/superpacks_manifest.zip',
                                           'device_personalization_services/SmartRecOverviewChips__nasa_superpacks_manifest_ver=2022100601',
                                           'device_personalization_services/SmartRecPixelSearch__enable_aiai_tc_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_all_fallbacks=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_appaction_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_assistant_geller_data_index=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_assistant_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_assistant_personalized_deeplinks=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_assistant_vertical_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_chrometab_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_corpora_via_search_context=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_entity_annotation_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_entity_based_action_generation=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_feedback_ranking=false',
                                           'device_personalization_services/SmartRecPixelSearch__enable_gboard_suggestion=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_nasa_for_search=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_navigational_sites_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_screenshot_generator=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_screenshot_thumbnail_cache=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_search_on_contacts=true',
                                           'device_personalization_services/SmartRecPixelSearch__enable_search_on_files=false',
                                           'device_personalization_services/SmartRecPixelSearch__enable_spelling_correction=true',
                                           'device_personalization_services/SmartRecPixelSearch__spelling_checker_frequency_score_overrides_map={"8":-7}',
                                           'device_personalization_services/NowPlaying__ambient_music_apk_music_detector_min_score=0.45',
                                           'device_personalization_services/NowPlaying__ambient_music_download_album_art_via_astrea=false',
                                           'device_personalization_services/NowPlaying__ambient_music_enable_resource_download_logging=false',
                                           'device_personalization_services/NowPlaying__ambient_music_enhanced_metadata_shards_manifest=4003:https://storage.googleapis.com/music-iq-db/updatable_db_v4/20241015-000033/manifest.json',
                                           'device_personalization_services/NowPlaying__ambient_music_get_model_state_cooldown_seconds_cloud_search=9',
                                           'device_personalization_services/NowPlaying__ambient_music_index_manifest_17_09_02=3105:https://storage.googleapis.com/music-iq-db/updatable_db_v3/20241013-030037/manifest.json',
                                           'device_personalization_services/NowPlaying__ambient_music_matcher_match_threshold_17_09_02=1.0E-6',
                                           'device_personalization_services/NowPlaying__ambient_music_on_demand_enabled=true',
                                           'device_personalization_services/NowPlaying__ambient_music_on_demand_music_confidence=0.48',
                                           'device_personalization_services/NowPlaying__ambient_music_on_demand_search_use_new_opt_in_flow=false',
                                           'device_personalization_services/NowPlaying__ambient_music_show_album_art=false',
                                           'device_personalization_services/NowPlaying__ambient_music_support_dsp_model_tflite_p6=true',
                                           'device_personalization_services/NowPlaying__ambient_music_use_enhanced_matches_database=false',
                                           'device_personalization_services/NowPlaying__ambient_music_use_metadata_shards_database=false',
                                           'device_personalization_services/NowPlaying__ambient_music_use_yt_domain_fife_urls=false',
                                           'device_personalization_services/NowPlaying__cloud_api_allowed=true',
                                           'device_personalization_services/NowPlaying__create_shortcut_on_np_enabled=false',
                                           'device_personalization_services/NowPlaying__default_music_player_setting=false',
                                           'device_personalization_services/NowPlaying__dsp_model_checksum_enabled=true',
                                           'device_personalization_services/NowPlaying__favorites_enabled=true',
                                           'device_personalization_services/NowPlaying__feature_users_count_enabled=true',
                                           'device_personalization_services/NowPlaying__handle_ambient_music_results_with_history=true',
                                           'device_personalization_services/NowPlaying__min_training_interval_millis=86400000',
                                           'device_personalization_services/NowPlaying__nnfp_v3_model_enabled=true',
                                           'device_personalization_services/NowPlaying__on_demand_enable_eager_prompt=true',
                                           'device_personalization_services/NowPlaying__on_demand_fingerprinter_being_setup_warning=true',
                                           'device_personalization_services/NowPlaying__on_demand_hide_if_fingerprinter_install_not_confirmed=true',
                                           'device_personalization_services/NowPlaying__on_demand_min_supported_aga_version=12.35.17',
                                           'device_personalization_services/NowPlaying__on_demand_retry_fingerprinter_install=true',
                                           'device_personalization_services/NowPlaying__shortcut_direct_create_enabled=false',
                                           'device_personalization_services/NowPlaying__youtube_export_enabled=true',
                                           'device_personalization_services/AdaptiveAudio__enable_adaptive_audio=true',
                                           'device_personalization_services/AdaptiveAudio__show_promo_notification=false',
                                           'device_personalization_services/AdaptiveAudio__use_silence_detector_state_bug_fix=true',
                                           'device_personalization_services/Attention__accel_sensor_enabled=false',
                                           'device_personalization_services/Attention__accel_sensor_threshold_mss=0.2',
                                           'device_personalization_services/Attention__enabled=true',
                                           'device_personalization_services/Attention__margin_horizontal_px=1000',
                                           'device_personalization_services/Attention__margin_vertical_px=1000',
                                           'device_personalization_services/Attention__proximity_sensor_enabled=false',
                                           'device_personalization_services/OverviewFederatedAnalytics__enable_fa=false',
                                           'device_personalization_services/OverviewFederatedAnalytics__enable_min_training_interval=false',
                                           'device_personalization_services/OverviewFederatedAnalytics__enable_non_synthetic_logs=false',
                                           'device_personalization_services/Autofill__enable=false',
                                           'device_personalization_services/Autofill__enable_fa=false',
                                           'device_personalization_services/Fedex__enable_fedex=false',
                                           'device_personalization_services/Logging__enable_aiai_clearcut_logging=false',
                                           'device_personalization_services/NotificationAssistant__enable_service=false',
                                           'device_personalization_services/VisualCortex__enable=false',
                                           'notification_assistant/generate_actions=true',
                                           'notification_assistant/generate_replies=true']))
        r.add(StringArray('config_globallyDisabledComponents', [
            'com.google.android.as/com.google.intelligence.sense.ambientmusic.history.HistoryContentProvider',
            'com.google.android.as/com.google.intelligence.sense.ambientmusic.history.HistoryActivity',
            'com.google.android.as/com.google.intelligence.sense.ambientmusic.AmbientMusicSettingsActivity',
            'com.google.android.as/com.google.intelligence.sense.ambientmusic.AmbientMusicNotificationsSettingsActivity',
            'com.google.android.as/com.google.intelligence.sense.ambientmusic.AmbientMusicSetupWizardActivity']))
        return r

    @staticmethod
    def get_settings_services_resources(android_version):
        r = Resources()
        r.add(String('config_systemSettingsIntelligence', 'com.google.android.settings.intelligence'))
        if float(android_version) >= 14:
            r.add(String('config_settingsintelligence_package_name', 'com.google.android.settings.intelligence'))
            r.add(
                String('config_settingsintelligence_log_action', 'com.google.android.settings.intelligence.LOG_BRIDGE'))
        return r

    @staticmethod
    def get_google_clock_resources():
        r = Resources()
        r.add(String('widget_default_package_name', 'com.google.android.deskclock'))
        r.add(String('widget_default_class_name', 'com.android.alarmclock.DigitalAppWidgetProvider'))
        r.add(String('config_dreamsDefaultComponent', 'com.google.android.deskclock/com.android.deskclock.Screensaver'))
        return r

    @staticmethod
    def get_cinematic_effect_resources():
        r = Resources()
        r.add(String('config_defaultWallpaperEffectsGenerationService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.wallpapereffects.AiAiWallpaperEffectsGenerationService'))
        return r

    @staticmethod
    def get_google_files_resources():
        r = Resources()
        r.add(String('config_systemFilePicker', 'com.google.android.apps.nbu.files'))
        r.add(String('config_sceenshotWorkProfileFilesApp', 'com.google.android.apps.nbu.files/com.google.android.apps.nbu.files.home.HomeActivity'))
        return r

    @staticmethod
    def get_google_wallpaper_resources():
        r = Resources()
        r.add(String('config_wallpaper_picker_package', 'com.google.android.apps.wallpaper'))
        r.add(String('config_wallpaperCropperPackage', 'com.google.android.apps.wallpaper'))
        r.add(String('config_wallpaper_picker_class', 'com.google.android.apps.wallpaper.picker.CategoryPickerActivity'))
        r.add(String('config_styles_and_wallpaper_picker_class', 'com.android.customization.picker.CustomizationPickerActivity'))
        return r

    @staticmethod
    def get_google_partner_setup_resources():
        r = Resources()
        r.add(String('config_deviceProvisioningPackage', 'com.google.android.apps.work.oobconfig'))
        return r

    @staticmethod
    def get_google_sounds_resources():
        r = Resources()
        r.add(String('config_sound_picker_package_name', 'com.google.android.soundpicker'))
        return r
