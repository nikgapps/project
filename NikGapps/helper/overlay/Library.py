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
        r.add(StringArray('config_locationExtraPackageNames', ['com.google.android.gms.location.history']))
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
        r.add(String('exit_to_action_in_initial_setup', 'com.google.android.apps.nexuslauncher/com.android.quickstep.action.GESTURE_ONBOARDING_ALL_SET'))
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
        r.add(Bool('config_allowDisablingAssistDisclosure', True))
        return r

    @staticmethod
    def get_youtube_music_resources():
        r = Resources()
        r.add(String('config_defaultMusic', 'com.google.android.apps.youtube.music'))
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
        r.add(StringArray('configs_base', ['device_personalization_services/Captions__enable_augmented_modality=true',
                                           'device_personalization_services/Captions__enable_augmented_modality_input=true',
                                           'device_personalization_services/Captions__enable_augmented_modality_language_detection=true',
                                           'device_personalization_services/Captions__enable_augmented_music=false',
                                           'device_personalization_services/Captions__enable_clearcut_logging=true',
                                           'device_personalization_services/Captions__enable_language_detection=true',
                                           'device_personalization_services/Captions__enable_punctuations=true',
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
                                           'device_personalization_services/EchoSmartspace__ring_channels_regex=4_ding_channel_notification\d+',
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
                                           'device_personalization_services/NotificationAssistant__enable_service=true',
                                           'device_personalization_services/NotificationAssistant__enable_upgrade_importance=true',
                                           'device_personalization_services/NotificationAssistant__importance_model_download_url=https://www.gstatic.com/android/notifications/importance/v1/manifest.json',
                                           'device_personalization_services/NotificationAssistant__importance_model_type=channel_stats',
                                           'device_personalization_services/NotificationAssistant__importance_model_version=1',
                                           'device_personalization_services/NotificationAssistant__max_importance_variance=0.5',
                                           'device_personalization_services/Overview__enable_lens_r_overview_translate_action=true',
                                           'device_personalization_services/Translate__blue_chip_translate_enabled=true',
                                           'device_personalization_services/Translate__copy_to_translate_enabled=true',
                                           'device_personalization_services/Translate__replace_auto_translate_copied_text_enabled=true',
                                           'device_personalization_services/Translate__translation_service_enabled=true',
                                           'device_personalization_services/Translate__enable_chronicle_migration=true',
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
    def get_settings_services_resources():
        r = Resources()
        r.add(String('config_systemSettingsIntelligence', 'com.google.android.settings.intelligence'))
        return r

    @staticmethod
    def get_google_clock_resources():
        r = Resources()
        r.add(String('widget_default_package_name', 'com.google.android.deskclock'))
        return r

    @staticmethod
    def get_cinematic_effect_resources():
        r = Resources()
        r.add(String('config_defaultWallpaperEffectsGenerationService',
                     'com.google.android.as/com.google.android.apps.miphone.aiai.app.wallpapereffects.AiAiWallpaperEffectsGenerationService'))
        return r
