# NikGapps Package Pipeline

Independent migration and publishing tools for legacy NikGapps package
repositories. See `docs/architecture.md` for the data model and operating
workflow.

Run from the parent workspace:

```text
python -m nikgapps_package_pipeline --help
```

## Upgrade a stable Android tree

The upgrade command preserves the AppSet/package layout of an existing stable
tree while resolving renamed APKs by Android package ID. With
`--carry-forward-missing`, it starts from the known-good template, replaces APK
directories and exact-path dependent files available in the target image, and
records every retained package/file in `upgrade-report.json` for review. It can
also generate and compile the Android-version-specific overlays in the same run.

```text
python -m nikgapps_package_pipeline upgrade \
  --template ../16_stable \
  --baseline-firmware ../16_mustang_260205 \
  --target-firmware ../17_mustang_260805 \
  --output ../17_stable \
  --carry-forward-missing \
  --android-version 17 \
  --overlay-source ../overlays_17_source \
  --overlay-output ../overlays_17
```

Android 17 overlays can be generated and compiled locally with:

```text
python -m NikGapps.overlay_control --android-version 17 \
  --source-dir ../overlays_17_source --output-dir ../overlays_17
```

Overlay compilation requires Java and Android SDK Build-Tools (`zipalign`) on
`PATH`. In PyCharm, add the chosen SDK `build-tools/<version>` directory to the
Run Configuration's `PATH`, or launch PyCharm from a terminal where `zipalign`
is available. The upgrade command never publishes to GitLab.

## Release-scoped metadata

`catalog.json` stores immutable package versions, their AppSet associations,
detected ABI restrictions, and `supportedAndroidVersions`. Android/channel
selection is stored separately in `releases/index.json`. Each publication adds
an immutable manifest under
`releases/android-<version>/<architecture>/<channel>/<release-id>.json`; that
manifest pins package versions and the complete AppSet snapshot for the release.

The index keeps a `latest` pointer for each Android version, channel, and build
architecture plus append-only release history. Set `PACKAGE_RELEASE_ID` to a
historical ID to reproduce an older build. Packages without native ABI content
have no architecture restriction or ABI component in their version key.
