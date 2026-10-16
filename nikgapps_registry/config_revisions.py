"""Version configuration structure independently from APK content."""
import hashlib
import json
import re


def template_with_version(content: str, version: int) -> str:
    return re.sub(r"^Version=.*$", f"Version={version}", content, flags=re.MULTILINE)


def structural_definitions(definitions):
    """Ignore APK-derived compatibility data, not user-facing definitions."""
    if not isinstance(definitions, dict):
        return definitions
    if "packages" in definitions:
        return {**definitions, "packages": [structural_definitions(p) for p in definitions["packages"]]}
    if "id" in definitions:
        return {key: value for key, value in definitions.items()
                if key not in {"packageName", "android", "architectures", "defaultPartition"}}
    return definitions


def definition_fingerprint(content: str, definitions=None, *, legacy=False) -> str:
    assignments = [line.strip() for line in content.splitlines()
                   if line.strip() and not line.lstrip().startswith("#")
                   and not line.startswith("Version=")]
    payload = {"config": assignments, "definitions": (definitions if legacy else structural_definitions(definitions)) or {}}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def next_config_version(content: str, base_version: int, previous: dict, fingerprint: str, definitions=None) -> int:
    current = max(base_version, int(previous.get("version", base_version)))
    old_fingerprint = previous.get("definitionFingerprint")
    if old_fingerprint and previous.get("fingerprintSchemaVersion", 1) == 1 and "definitions" in previous:
        # Reconstruct the old hash using today's config text. This detects real
        # config edits while migrating stored APK-derived definitions in place.
        same_config = definition_fingerprint(content, previous["definitions"], legacy=True) == old_fingerprint
        same_structure = structural_definitions(previous["definitions"]) == structural_definitions(definitions)
        return current if same_config and same_structure else max(base_version, int(previous["version"]) + 1)
    if old_fingerprint:
        return max(base_version, int(previous.get("version", base_version)) + 1) if old_fingerprint != fingerprint else current
    # Migrate legacy metadata without incrementing unchanged templates.
    legacy = hashlib.sha256(template_with_version(content, current).encode()).hexdigest()
    old_digest = previous.get("template", {}).get("sha256")
    return max(base_version, int(previous.get("version", base_version)) + 1) if old_digest and old_digest != legacy else current


def release_definitions(metadata, android, channel="stable", architecture="arm64-v8a"):
    index_path = metadata / "releases/index.json"
    if not index_path.exists():
        return None
    index = json.loads(index_path.read_text())
    release_id = index.get("latest", {}).get(str(android), {}).get(channel, {}).get(architecture)
    summary = next((r for r in index.get("releases", []) if r["id"] == release_id), None)
    if summary is None:
        return None
    release = json.loads((metadata / summary["manifest"]).read_text())
    catalog = json.loads((metadata / "catalog.json").read_text())
    packages = []
    for item in catalog["packages"]:
        locked = release["packages"].get(item["id"])
        if not locked:
            continue
        version = item["versions"][locked["version"]]
        packages.append({"id": item["id"], "name": item["name"],
                         "dependencies": item.get("dependencies", []),
                         "packageName": version.get("packageName"),
                         "android": {key: version.get("android", {}).get(key) for key in ("minApi", "maxApi")},
                         "architectures": version.get("architectures"),
                         "defaultPartition": version.get("defaultPartition"),
                         "selectable": item.get("selectable"), "internal": item.get("internal")})
    return {"appSets": release["appSets"], "packages": sorted(packages, key=lambda p: p["id"])}


def attach_config_to_release(metadata, android, channel, architecture, entry):
    path = metadata / "releases/index.json"
    index = json.loads(path.read_text())
    release_id = index["latest"][str(android)][channel][architecture]
    summary = next(r for r in index["releases"] if r["id"] == release_id)
    fields = {"configVersion": entry["version"], "definitionFingerprint": entry["definitionFingerprint"],
              "configTemplate": entry["template"], "packageDefinitions": entry.get("packageDefinitions", {}),
              "configSettings": entry.get("configSettings", [])}
    summary.update(fields)
    release_path = metadata / summary["manifest"]
    release = json.loads(release_path.read_text())
    release.update(fields)
    release_path.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")
    path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
