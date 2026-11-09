"""Android 17 Go is a deterministic overlay on the single Core source tree."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from NikGapps.helper.Assets import Assets

SHARED_CORE_PACKAGES = frozenset({"GmsCore", "GooglePlayStore", "GoogleServicesFramework"})


def core_source_appset(appset, package, android_version):
    return "Core" if float(android_version) >= 17 and appset == "CoreGo" and package in SHARED_CORE_PACKAGES else appset


def generated_go_files(core: Path, output: Path) -> dict[str, Path]:
    """Write only Go-specific XML. APKs, libraries and shared files stay in Core."""
    recipe = json.loads(Path(Assets.cwd, "corego-android17.json").read_text(encoding="utf-8"))
    result = {}
    relative = "___etc___permissions/NikGapps-privapp-permissions-google-p.xml"
    tree = ET.parse(core / relative)
    for group in list(tree.getroot()):
        package = group.get("package")
        if package in recipe["removePermissionPackages"]:
            tree.getroot().remove(group)
            continue
        for permission in list(group):
            if permission.get("name") in recipe["removePermissions"].get(package, []):
                group.remove(permission)
    destination = output / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding="utf-8", xml_declaration=True)
    result[relative] = destination
    for relative, text in recipe["additionalFiles"].items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8", newline="\n")
        result[relative] = destination
    return result
