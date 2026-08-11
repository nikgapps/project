# Architecture and migration workflow

## Storage model

The suggested GitLab project name is `nikgapps-package-catalog`.

The Git repository contains only:

- `catalog.json`;
- `appsets.json`;
- immutable release lock files;
- schemas, configuration, and migration/build code.

The Generic Package Registry contains one immutable, prebuilt NikGapps package
ZIP for every distinct package payload. APKs and dependencies are not committed
to Git. Each ZIP is ready to be nested under `AppSet/<name>/<package>.zip` and
contains encoded payload paths, `installer.sh`, `uninstaller.sh`, and
`package.json`.

## Legacy translation

The scanner treats the first two directory levels as `AppSet/Package`.
Everything below the package is payload. Every `___` sequence translates to a
path separator:

```text
Core/GmsCore/___priv-app___PrebuiltGmsCoreVic/PrebuiltGmsCoreVic.apk
```

becomes this package ZIP entry:

```text
___priv-app___PrebuiltGmsCoreVic/PrebuiltGmsCoreVic.apk
```

`package.json` records `"defaultPartition": "product"`. A different
partition is configured per package; it is not guessed from the legacy path.
An encoded segment that explicitly contains `system`, such as
`___system___etc`, remains `system/etc` below the default payload and can be
handled by the compatibility builder as an explicit partition path.

See `16_stable-assessment.md` for the read-only validation results from the
supplied repository.

AppSets contain package IDs rather than copied package bytes. Identical
packages appearing in `Core` and `CoreGo` become one artifact referenced by
both sets.

## Artifact identity

Registry coordinates follow:

```text
package name:    nikgapps-<stable-id>
package version: <versionCode>-<architecture>-<content hash>

## Architecture and device inheritance

`catalog.json.defaults` defines the normal compatibility values. The generated
catalog currently defaults to `architectures: ["arm64-v8a"]` and
`deviceTypes: ["phone"]`. Package versions omit values equal to those defaults.
An explicitly empty `architectures` override means the package is ABI-neutral;
alternate ABIs and tablet-only packages store only their overrides. Configure
these with top-level `architecture` / `defaultDeviceType`, or per-package
`architectures` / `deviceTypes`. Consumers must expand defaults before checking
compatibility.
file name:       <stable-id>.zip
```

Including a build-contract hash prevents a changed payload, partition,
installer rule, removal rule, or generated permission from overwriting an
existing artifact even when APK metadata is unchanged. Channels such as
`stable` and `candidate` point to immutable versions and are not part of the
artifact identity.

## Commands

Create artifacts and metadata without network writes:

```powershell
python -m nikgapps_package_pipeline migrate `
  --input D:\WORKSPACE\PYTHON\16_STABLE `
  --output D:\WORKSPACE\PYTHON\16_STABLE_MIGRATED `
  --config nikgapps_package_pipeline\nikgapps-pipeline.example.json `
  --android-version 16 `
  --platform-api 36 `
  --channel stable `
  --aapt2 C:\Android\Sdk\build-tools\36.0.0\aapt2.exe `
  --artifact-base-url https://gitlab.com/api/v4/projects/123/packages/generic
```

Create a GitLab project:

```powershell
$env:GITLAB_TOKEN = "..."
python -m nikgapps_package_pipeline create-project `
  --name nikgapps-package-catalog `
  --namespace-id 12345 `
  --visibility public
```

Migrate and publish:

```powershell
$env:GITLAB_TOKEN = "..."
python -m nikgapps_package_pipeline migrate `
  --input D:\WORKSPACE\PYTHON\16_STABLE `
  --output D:\WORKSPACE\PYTHON\16_STABLE_MIGRATED `
  --config nikgapps_package_pipeline\nikgapps-pipeline.example.json `
  --gitlab-project 123456 `
  --publish `
  --aapt2 C:\Android\Sdk\build-tools\36.0.0\aapt2.exe
```

`--create-project --publish` combines project creation and publication. These
flags intentionally require `GITLAB_TOKEN`; no credential is stored in code.
Publishing uploads each package ZIP to the Generic Package Registry and commits
the generated metadata to the repository's `main` branch. Use
`--metadata-branch` if the project uses another branch.

To recreate input for the existing builder during the transition, add:

```text
--compat-output D:\WORKSPACE\PYTHON\16_STABLE_COMPAT
```

This expands the newly built artifacts back to the original
`AppSet/Package/___path` convention. It is optional because it duplicates
payload bytes locally. Point the existing builder's `APK_SOURCE` at that
directory. The source repository is never modified.

## Output

```text
16_STABLE_MIGRATED/
├── artifacts/
│   └── gms_core/
│       └── 252832000-arm64-v8a-<hash>/
│           └── gms_core.zip
└── metadata/
    ├── catalog.json
    ├── appsets.json
    └── releases/
        └── android-16-arm64-v8a.json
```

After verified publication, `artifacts/` is disposable. The registry is the
authoritative binary store. Preserve and commit `metadata/`.

## Updating a package

Put the candidate APK into a separate legacy input checkout or staging tree,
run migration with `--channel candidate`, and publish the new immutable
artifact. After testing, change the catalog channel pointers; do not rebuild or
overwrite the artifact. Release locks continue referring to exact hashes.

## Compatibility builder

The existing GApps builder can consume the new format through an adapter:

1. resolve AppSet package IDs from `appsets.json`;
2. resolve a channel or release lock through `catalog.json`;
3. download and verify each artifact;
4. cache it by artifact SHA-256;
5. validate `package.json` and the files listed in it;
6. place the already-built package ZIP under the chosen AppSet in the final ZIP.

## Package build metadata

Package overrides can describe installer behavior that is not present as a
physical source file:

```json
{
  "packages": {
    "Core/GmsCore": {
      "removeFiles": ["GmsCore"],
      "removeOverlays": [],
      "privilegedPermissions": ["android.permission.READ_DEVICE_CONFIG"],
      "cleanFlashOnly": false,
      "additionalInstallerScript": "# trusted NikGapps shell fragment",
      "validationScript": "find_install_mode",
      "addonIndex": "09"
    }
  }
}
```

When `privilegedPermissions` is present, migration generates and packages the
corresponding `etc/permissions/<android-package-name>.xml`. Existing APKs,
split APKs, overlays, permission XML, framework libraries, native libraries,
and other supporting files are classified in both `package.json` and the
catalog version metadata.

This adapter can be added without changing or importing the migration package.
