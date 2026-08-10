# `16_STABLE` migration assessment

Read-only inspection of `D:\WORKSPACE\PYTHON\16_STABLE` found:

- Android version: 16;
- platform API represented by the release: 36;
- channel: stable;
- AppSet directories: 49;
- package directories: 78;
- unique stable IDs: 73;
- payload files: 215;
- source payload size: approximately 3.221 GiB;
- primary APKs successfully inspected with `aapt2`: 76;
- file-only packages: `Core/ExtraFiles` and `CoreGo/ExtraFilesGo`;
- ambiguous primary APKs: none;
- malformed primary APKs: none.

The following five packages are byte-identical duplicates between `Core` and
`CoreGo` and can be represented by one artifact with two AppSet memberships:

- `GmsCore`;
- `GoogleCalendarSyncAdapter`;
- `GoogleContactsSyncAdapter`;
- `GooglePlayStore`;
- `GoogleServicesFramework`.

The following Android package names intentionally occur in different logical
packages:

- `com.google.android.onetimeinitializer`;
- `com.google.android.apps.restore`;
- `com.google.android.setupwizard`.

They are Pixel/non-Pixel alternatives and should keep distinct stable IDs.
Android package-name uniqueness must therefore be enforced within a resolved
AppSet/release selection, not globally across the entire repository.

Google Docs, Google Sheets, and Google Slides contain split APK dependencies.
Their non-`split_*` APK is the unambiguous primary APK; split APKs remain in the
same package artifact.

The example configuration explicitly records known `system_ext` defaults.
All other packages default to `product`. These values should be reviewed when
new packages or Android versions are introduced because a leading `___` does
not encode a partition.
