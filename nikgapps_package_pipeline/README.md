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
tree while resolving renamed APKs by Android package ID. Payload files are
copied only from the target Mustang extraction; missing Android 17 packages are
listed in `upgrade-report.json` instead of being silently carried over.

```text
python -m nikgapps_package_pipeline upgrade \
  --template ../16_stable \
  --baseline-firmware ../16_mustang_260205 \
  --target-firmware ../17_mustang_260805 \
  --output ../17_stable
```

Android 17 overlays can be generated and compiled locally with:

```text
python -m NikGapps.overlay_control --android-version 17 \
  --source-dir ../overlays_17_source --output-dir ../overlays_17
```
