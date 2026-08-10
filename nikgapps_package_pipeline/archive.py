from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from .errors import PipelineError
from .models import PayloadFile
from .util import json_data, safe_path

ZIP_TIME = (1980, 1, 1, 0, 0, 0)
ALREADY_COMPRESSED = {
    ".apk", ".zip", ".jar", ".gz", ".png", ".jpg", ".jpeg", ".webp",
    ".mp3", ".mp4", ".so", ".tflite",
}


def _write_entry(archive: zipfile.ZipFile, name: str, data: bytes, compress: int) -> None:
    safe_path(name)
    info = zipfile.ZipInfo(name, ZIP_TIME)
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.compress_type = compress
    archive.writestr(info, data, compress_type=compress, compresslevel=9)


def write_package_zip(
    destination: Path,
    files: list[PayloadFile],
    manifest: dict[str, Any],
    *,
    pretty: bool = True,
) -> None:
    if any(item.path in {"package.json", "installer.sh", "uninstaller.sh"} for item in files):
        raise PipelineError("Payload collides with reserved package.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w") as archive:
        for item in sorted(files, key=lambda value: value.path):
            compression = (
                zipfile.ZIP_STORED
                if item.source.suffix.casefold() in ALREADY_COMPRESSED
                else zipfile.ZIP_DEFLATED
            )
            _write_entry(archive, encode_builder_path(item.path), item.source.read_bytes(), compression)
        for generated in sorted(manifest.get("generatedFiles", []), key=lambda value: value["path"]):
            _write_entry(
                archive,
                encode_builder_path(generated["path"]),
                generated["content"].encode("utf-8"),
                zipfile.ZIP_DEFLATED,
            )
        _write_entry(archive, "installer.sh", package_installer(manifest).encode(), zipfile.ZIP_DEFLATED)
        _write_entry(archive, "uninstaller.sh", package_uninstaller(manifest).encode(), zipfile.ZIP_DEFLATED)
        _write_entry(archive, "package.json", json_data(manifest, pretty), zipfile.ZIP_DEFLATED)


def encode_builder_path(path: str) -> str:
    """Encode an install path using the nested-package format used by NikGapps."""
    safe_path(path)
    parts = path.split("/")
    return "___" + "___".join(parts[:-1]) + "/" + parts[-1]


def _lines(values: list[str]) -> str:
    return "\n".join(values)


def _legacy_asset(name: str) -> str:
    path = Path(__file__).resolve().parent.parent / "NikGapps" / "helper" / "assets" / name
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PipelineError(f"Cannot read legacy package template {path}: {exc}") from exc


def package_installer(manifest: dict[str, Any]) -> str:
    install = manifest["install"]
    apk = manifest.get("apk") or {}
    file_list = [item["archivePath"] for item in manifest["files"]]
    extra = install.get("additionalInstallerScript") or ""
    extra_block = f"{extra}\n" if extra else ""
    validation = install.get("validationScript") or "find_install_mode"
    remove_files = [value for value in install["removeFiles"] if value.strip()]
    remove_overlays = [value for value in install["removeOverlays"] if value.strip()]
    remove_files_block = "".join(f"{value}\n" for value in remove_files)
    remove_overlays_block = "".join(f"{value}\n" for value in remove_overlays)
    file_list_block = "".join(f"{value}\n" for value in file_list)
    folders: list[str] = []
    for row in manifest["files"]:
        parts = row["path"].split("/")[:-1]
        for index in range(1, len(parts) + 1):
            folder = "/".join(parts[:index])
            if parts and parts[0] not in {"system", "vendor", "product", "system_ext", "overlay"} and folder not in folders:
                folders.append(folder)
    make_dirs = "".join(f'   make_dir "{folder}"\n' for folder in folders)
    return _legacy_asset("installer.sh") + f'''# Initialize the variables
default_partition="{manifest["defaultPartition"]}"
clean_flash_only="{str(install["cleanFlashOnly"]).lower()}"
product_prefix=$(find_product_prefix "$install_partition")
title="{install["title"]}"
package_title="{install["packageTitle"]}"
pkg_size="{install["payloadSize"]}"
package_name="{manifest.get("packageName") or ""}"
packagePath=install{install["packageTitle"]}Files
deleteFilesPath=delete{install["packageTitle"]}Files
propFilePath=$(get_prop_file_path $package_title)

remove_aosp_apps_from_rom="
{remove_files_block}"

delete_overlays="
{remove_overlays_block}"

file_list="
{file_list_block}"

remove_overlays() {{
   for i in $delete_overlays; do
       delete_overlays "$i" "$propFilePath" "$package_title" 
   done
}}

remove_existing_package() {{
   # remove the existing folder for clean install of {install["packageTitle"]}
   delete_package "{install["title"]}" "$package_title" 
}}

remove_aosp_apps() {{
   # Delete the folders that we want to remove with installing {install["packageTitle"]}
   for i in $remove_aosp_apps_from_rom; do
       RemoveAospAppsFromRom "$i" "$propFilePath" "$package_title" 
   done
}}

install_package() {{
   remove_existing_package
   remove_aosp_apps
   remove_overlays
   # Create folders and set the permissions
{make_dirs}
   delete_prop_lines "$propFilePath"

   # Copy the files and set the permissions
   for i in $file_list; do
       install_file "$i"
   done

{extra_block}   chmod 755 "$COMMONDIR/addon.sh";
   update_prop "$propFilePath" "install" "$propFilePath" "{install["packageTitle"]}" 
   . $COMMONDIR/addon.sh "{install["packageTitle"]}" "$propFilePath" "{install["addonIndex"]}"
   copy_file "$propFilePath" "$logDir/addonfiles/$package_title.prop"
}}

{validation}

'''


def package_uninstaller(manifest: dict[str, Any]) -> str:
    install = manifest["install"]
    file_list = [item["archivePath"] for item in manifest["files"]]
    return _legacy_asset("uninstaller.sh") + f'''

# Initialize the variables
uninstall_addon=$1
clean_flash_only="{str(install["cleanFlashOnly"]).lower()}"
title="{install["title"]}"
package_title="{install["packageTitle"]}"
package_name="{manifest.get("packageName") or ""}"

file_list="
{_lines(file_list)}
"

uninstall_package
'''
