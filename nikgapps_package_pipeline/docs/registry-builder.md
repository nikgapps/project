# Building NikGapps from the package registry

The existing release and export pipeline remains responsible for the final
flashable ZIP. Registry mode replaces only the APK source preparation step.

## Configuration

These values may be placed in `NikGapps/.env`:

```text
PACKAGE_SOURCE=registry
PACKAGE_CHANNEL=stable
PACKAGE_CATALOG_URL=https://gitlab.com/nikgapps/nikgapps-package-catalog/-/raw/main/catalog.json
PACKAGE_APPSETS_URL=https://gitlab.com/nikgapps/nikgapps-package-catalog/-/raw/main/appsets.json
PACKAGE_CACHE=D:\WORKSPACE\PYTHON\nikgapps-package-cache
PACKAGE_CHANNEL_OVERRIDES={}
```

`PACKAGE_SOURCE=git` retains the old source repository behavior.

Per-package channel selection uses a JSON object:

```text
PACKAGE_CHANNEL_OVERRIDES={"you_tube":"canary","gms_core":"beta"}
```

## Core test build

Run module `NikGapps.main` with:

```text
--packageSource registry --packageChannel stable --androidVersion 16 --packageList core --arch arm64
```

The adapter downloads only Core artifacts, verifies SHA-256, caches each ZIP by
checksum, resolves hidden GmsCore support packages, and materializes a versioned
legacy source tree. It accepts both the original payload-only artifacts and the
new prebuilt package ZIP format during migration. New Android builds can place
the prebuilt ZIP directly in the final AppSet instead of regenerating it.

Overlays continue to come from the established overlay repository until they
are migrated into catalog artifacts.
