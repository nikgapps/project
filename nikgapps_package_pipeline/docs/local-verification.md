# Local package and Android verification

The project defaults target the current Android 16 stable workflow:

```text
input:          D:\workspace\python\16_stable
output:         D:\workspace\python\16_STABLE_PREBUILT_RELEASE
configuration:  nikgapps-pipeline.example.json
Android:        16 (platform API derived as 36)
channel:        stable
GitLab project: 85036487
branch:         main
aapt2:          bundled nikassets executable
```

Consequently, `python -m nikgapps_package_pipeline migrate` performs a local
build and `python -m nikgapps_package_pipeline migrate --publish` builds,
uploads, and commits metadata. Remote writes always require the explicit
`--publish` switch.

## 1. Build one package without publishing

From `D:\workspace\python\project`:

```powershell
$aapt2 = 'D:\workspace\python\nikassets\nikassets\helper\assets\bin\Windows\aapt2.exe'
$preview = 'D:\workspace\python\PACKAGE_REGISTRY_PREVIEW'

python -m nikgapps_package_pipeline migrate `
  --input D:\workspace\python\16_stable `
  --output $preview `
  --config nikgapps_package_pipeline\nikgapps-pipeline.example.json `
  --android-version 16 `
  --platform-api 36 `
  --channel stable `
  --package GoogleFeedback `
  --aapt2 $aapt2 `
  --artifact-base-url https://example.invalid/packages/generic
```

Omit `--package GoogleFeedback` to generate every package. This command does
not contact or modify GitLab because `--publish` is absent.

## 2. Inspect and verify a generated package

```powershell
$packageZip = Get-ChildItem "$preview\artifacts" -Recurse -Filter *.zip |
  Select-Object -First 1

tar -tf $packageZip.FullName
tar -xOf $packageZip.FullName package.json
Get-FileHash $packageZip.FullName -Algorithm SHA256
```

The ZIP must contain `installer.sh`, `uninstaller.sh`, `package.json`, and the
encoded payload entries declared by `files[].archivePath`. Check that:

- `packageName`, `versionName`, and `versionCode` match the primary APK;
- `android` and `architectures` match the intended device;
- every file has `path`, `archivePath`, `installPath`, `sha256`, `size`, and
  `type`;
- `install` contains partition, size, removal, permission, clean-flash, and
  addon behavior;
- the version in `metadata/catalog.json` contains the same `files` and
  `install` data;
- the artifact SHA-256 and size in the catalog match the ZIP.

## 3. Configure package-specific installer data

Add overrides to the pipeline configuration when behavior cannot be inferred
from the source tree:

```json
{
  "packages": {
    "Core/GmsCore": {
      "removeFiles": ["PrebuiltGmsCoreQt", "PrebuiltGmsCoreRvc", "GmsCore"],
      "removeOverlays": [],
      "privilegedPermissions": ["android.permission.READ_DEVICE_CONFIG"],
      "cleanFlashOnly": false,
      "validationScript": "find_install_mode",
      "addonIndex": "09"
    }
  }
}
```

`privilegedPermissions` creates a real
`etc/permissions/<packageName>.xml` inside the package. Files already present
under the package's source directory—including APK splits, overlays,
permission XML, framework JARs, native libraries, and supporting files—are
included and classified automatically.

## 4. Run Python tests

```powershell
python -m unittest `
  tests_package_pipeline.test_pipeline `
  tests_package_pipeline.test_consumer -v
```

## 5. Run Android tests

From `D:\workspace\android\NikGapps`:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\AndroidStudio\jbr'
.\gradlew.bat testDebugUnitTest --no-daemon
```

Build a debug APK with:

```powershell
.\gradlew.bat assembleDebug --no-daemon
```

The APK is written under `app\build\outputs\apk\debug`.

## 6. Test the app against local metadata

For an emulator, serve the preview directory:

```powershell
Set-Location $preview\metadata
python -m http.server 8080
```

An emulator reaches the host as `http://10.0.2.2:8080`. A physical device must
use the computer's LAN address. Clear the app cache after changing metadata if
testing cache fallback behavior.

The production catalog URLs currently live in `CatalogRepository.kt`. Before
local HTTP testing, use a debug-only URL override or temporarily change those
constants; do not ship a release build pointing to the local server.

## 7. Publish after verification

```powershell
$env:GITLAB_TOKEN = '<token>'
python -m nikgapps_package_pipeline migrate `
  --input D:\workspace\python\16_stable `
  --output D:\workspace\python\PACKAGE_REGISTRY_RELEASE `
  --config nikgapps_package_pipeline\nikgapps-pipeline.example.json `
  --android-version 16 `
  --platform-api 36 `
  --channel canary `
  --aapt2 $aapt2 `
  --gitlab-project 85036487 `
  --publish
```

Publish to `canary` first. After device testing, promote the exact immutable
version key to beta and stable by changing channel pointers; do not rebuild or
overwrite the registry artifact.

The `--channel` command-line value takes precedence over the reusable config
file, so the same package configuration can publish all three channels.

Existing payload-only registry versions can still be consumed by the Python
compatibility adapter, but the Android final-ZIP builder requires the new
prebuilt-package metadata. Republish packages into canary before enabling the
new Android build flow for users.

## Reset the Generic Package Registry

First run a read-only preview:

```powershell
python -m nikgapps_package_pipeline reset-registry
```

It lists every Generic Registry package and deletes nothing. After reviewing
the exact list, permanently remove them with:

```powershell
python -m nikgapps_package_pipeline reset-registry --confirm-project 85036487
```

This operation cannot be undone. It does not delete source repository files.
Immediately rebuild every stable package and replace historical metadata:

```powershell
python -m nikgapps_package_pipeline migrate --publish --fresh-metadata --verbose
```

Or reset once and sync Android 16 and 17 with one command:

```powershell
python -m nikgapps_package_pipeline reset-and-sync `
  --confirm-project 85036487 `
  --android-version 16,17 `
  --verbose
```

The project confirmation is mandatory. The command deletes Generic Registry
packages once, generates fresh metadata for the first release, then merges each
additional release into the same catalog and release index. It discovers
`<version>_stable` and `overlays_<version>` beside the `project` directory and
uses `MULTI_RELEASE_PREVIEW` there as its output. Use `--android-version 17` to
reset and publish only Android 17. Because reset applies to the whole registry,
use `16,17` whenever both releases must remain available. `--release` remains
available as an advanced override for nonstandard directory layouts.

Do not use `--fresh-metadata` for ordinary incremental package or channel
updates. It exists specifically for a complete registry reset followed by a
complete source migration.
