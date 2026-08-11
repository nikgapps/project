# NikGapps Registry Publisher

This module turns a legacy `AppSet/Package` source tree into individual,
self-describing ZIP packages, uploads them to the GitLab Generic Package
Registry, and commits `catalog.json` plus `appsets.json` to the same GitLab
project. The Android app can resolve packages entirely from that metadata.

## Authentication

Set `GITLAB_TOKEN` in the environment or in `NikGapps/.env`. The token needs
API access, permission to upload/delete packages, and permission to commit to
the metadata branch.

## Preview a reset

```powershell
python -m nikgapps_registry reset --project 85036487
```

## Permanently clear the Generic Package Registry

```powershell
python -m nikgapps_registry reset --project 85036487 --confirm-project 85036487
reset --project 85036487 --confirm-project 85036487
```

Reset intentionally leaves repository files untouched. Use `sync --fresh`
immediately afterwards so old catalog history is not reused.

## Reset and sync in one command

The command discovers `<version>_stable` and `overlays_<version>` beside the
`project` directory and loads `GITLAB_TOKEN` from the normal environment or
the project/NikGapps `.env` locations:

```powershell
python -m nikgapps_registry reset-and-sync `
  --confirm-project 85036487 `
  --android-version 16,17 `
  --verbose
```

Use `--android-version 17` for Android 17 only. Reset deletes the entire Generic
Registry only when multiple versions are explicitly supplied. With a single
version, the command performs a version-scoped incremental rebuild and preserves
every other Android version and its metadata.

## Fresh ZIP-only publication

```powershell
python -m nikgapps_registry --verbose sync `
  --source D:\workspace\python\16_stable `
  --work D:\workspace\python\16_REGISTRY_RELEASE `
  --project 85036487 `
  --android-version 16 `
  --arch arm64-v8a `
  --overlays D:\workspace\python\16_overlays `
  --busybox D:\workspace\python\project\.venv\Lib\site-packages\nikassets\helper\assets\busybox `
  --builder-assets D:\workspace\python\project\NikGapps\helper\assets `
  --channel stable `
  --fresh
  
 --verbose sync --source D:\workspace\python\16_stable --overlays D:\workspace\python\overlays_16 --work D:\workspace\python\16_REGISTRY_RELEASE --project 85036487 --android-version 16 --arch arm64-v8a --channel stable
```

## Incremental maintenance

Run the same command without `--fresh`. Existing remote metadata is downloaded
first, new immutable versions are merged into the catalog, and the selected
channel advances while prior versions remain available as fallback. Package
versions already present in GitLab are skipped, so this is the normal command
for republishing after source, permission, or overlay changes; a reset is not
required.

For the normal version-specific workflow, source, overlays, and work paths are
discovered automatically:

```powershell
python -m nikgapps_registry sync `
  --project 85036487 `
  --android-version 17 `
  --verbose
```

This updates only Android 17 pointers and adds its new immutable package
versions. Android 16 packages, pointers, and release history remain intact.

Use `--package PackageName` or `--package AppSet/PackageName` repeatedly for a
partial update. Use `--config` for package IDs, partitions, API constraints,
and exceptional source rules. Only ZIP artifacts are produced and uploaded;
TAR support is intentionally deferred.

`sync` publishes every static ZIP-builder file as an independent immutable
Generic Package and commits its URL, SHA-256, and size in
`builder-assets.json`. This includes scripts, configuration templates,
changelog, module metadata, and busybox. None are bundled in the Android APK,
so the Android project has no filesystem dependency on the Python checkout.

Registry uploads retry GitLab HTTP 429 and transient 5xx gateway failures up
to four times. If GitLab remains unavailable, rerun the same incremental sync;
already-published immutable package versions are skipped.

For Android 12.1 and newer, `--overlays` embeds APKs found under the legacy
`<PackageName>Overlay` folder into that package's ZIP. Privileged applications
are detected from their `priv-app` install path; their requested permissions
are read with `aapt2` and emitted as `etc/permissions/<packageName>.xml`.
