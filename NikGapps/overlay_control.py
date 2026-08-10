import argparse
import os
from pathlib import Path

from NikGapps.build.NikGappsOverlays import NikGappsOverlays
from NikGapps.helper.Args import Args
from niklibrary.helper.Cmd import Cmd
from niklibrary.helper.F import F
from niklibrary.helper.P import P
from niklibrary.helper.Statics import Statics
from niklibrary.git.Git import Git
from NikGapps.helper.overlay.Overlay import Overlay


ANDROID_PLATFORM_VERSIONS = {
    # niklibrary 0.28 predates Android 17. Keep the compatibility entry here
    # until the same mapping is available in the shared library.
    "17": {"sdk": "37", "code": "CinnamonBun"},
}


def register_android_platform(android_version):
    version = str(android_version)
    if version not in Statics.android_versions and version in ANDROID_PLATFORM_VERSIONS:
        Statics.android_versions[version] = ANDROID_PLATFORM_VERSIONS[version]


def build_local_overlays(android_version, source_dir, output_dir):
    """Generate and compile overlays locally without cloning or pushing repos."""
    register_android_platform(android_version)
    source_dir = os.path.abspath(source_dir)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    for overlay in NikGappsOverlays.get_overlay(android_version=android_version):
        overlay.build_apk_source(source_dir)
    built = []
    for folder in sorted(Path(source_dir).iterdir()):
        if not folder.is_dir() or not F.file_exists(os.path.join(str(folder), "apktool.yml")):
            continue
        overlay_path = Cmd().build_overlay(folder_name=str(folder))
        if not overlay_path:
            raise RuntimeError(f"Failed to build Android {android_version} overlay: {folder.name}")
        destination = os.path.join(output_dir, folder.name, f"{folder.name}.apk")
        F.copy_file(overlay_path, destination)
        F.remove_dir(os.path.join(str(folder), "dist"))
        F.remove_dir(os.path.join(str(folder), "build"))
        built.append(destination)
    return built


def overlay_control():
    args = Args()
    android_versions = args.get_android_versions()

    for android_version in android_versions:
        register_android_platform(android_version)
        repo_name = Statics.get_overlay_source_repo(android_version)
        repo_dir = Statics.get_overlay_source_directory(android_version)
        branch = "main"
        overlay_source_repo = Git(repo_dir)
        overlay_source_repo.clone_repo(repo_name, branch=branch)

        for overlay in NikGappsOverlays.get_overlay(android_version=android_version):
            overlay: Overlay
            overlay.build_apk_source(repo_dir)
            if overlay_source_repo.due_changes():
                print("Pushing due changes!")
                overlay_source_repo.git_push(commit_message=f"Updated {overlay.folder}!", push_untracked_files=True)

        if F.dir_exists(repo_dir):
            overlays_repo_name = Statics.get_overlay_repo(android_version)
            overlays_repo_dir = Statics.get_overlay_directory(android_version)
            overlay_repo = Git(overlays_repo_dir)
            overlay_repo.clone_repo(overlays_repo_name, branch="main")
            for folder in Path(repo_dir).iterdir():
                if str(folder).__contains__(".git") or str(folder).__contains__("README.md"):
                    continue
                cmd = Cmd()
                if not F.file_exists(os.path.join(str(folder), "apktool.yml")):
                    P.red(f"apktool.yml doesn't exist in {folder}")
                    continue
                overlay_path = cmd.build_overlay(folder_name=str(folder))
                if not overlay_path.__eq__(""):
                    print(f"{overlay_path} successfully built..")
                    print(
                        f"Copying to {os.path.join(overlays_repo_dir, str(Path(folder).name), f'{Path(folder).name}.apk')}")
                    F.copy_file(overlay_path, os.path.join(overlays_repo_dir,
                                                                str(Path(folder).name), f"{Path(folder).name}.apk"))
                    folder_to_remove = os.path.join(str(folder), "dist")
                    F.remove_dir(folder_to_remove)
                    folder_to_remove = os.path.join(str(folder), "build")
                    F.remove_dir(folder_to_remove)
                else:
                    print("Failed to build overlay")
            if overlay_repo.due_changes():
                print("Pushing due changes!")
                overlay_repo.git_push(commit_message="Updated Overlays!", push_untracked_files=True)
            else:
                print(f"{overlays_repo_dir} doesn't exist!")
        else:
            print(f"{repo_dir} doesn't exist!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build NikGapps resource overlays")
    parser.add_argument("--android-version")
    parser.add_argument("--source-dir")
    parser.add_argument("--output-dir")
    options = parser.parse_args()
    if options.android_version:
        if not options.source_dir or not options.output_dir:
            parser.error("--source-dir and --output-dir are required in local mode")
        paths = build_local_overlays(
            options.android_version, options.source_dir, options.output_dir
        )
        print(f"Built {len(paths)} overlays for Android {options.android_version}")
    else:
        overlay_control()
