import os
from pathlib import Path
from NikGapps.build.NikGappsOverlays import NikGappsOverlays
from NikGapps.helper.Args import Args
from NikGapps.helper.Cmd import Cmd
from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.Statics import Statics
from NikGapps.helper.git.Git import Git
from NikGapps.helper.overlay.Overlay import Overlay


def overlay_control():
    args = Args()
    android_versions = args.get_android_versions()

    for android_version in android_versions:
        repo_name = Statics.get_overlay_source_repo(android_version)
        repo_dir = Statics.get_overlay_source_directory(android_version)
        branch = "master"
        overlay_source_repo = Git(repo_dir)
        overlay_source_repo.clone_repo(repo_name, branch=branch)

        for overlay in NikGappsOverlays.get_overlay(android_version=android_version):
            overlay: Overlay
            overlay.build_apk_source(repo_dir)
            if overlay_source_repo.due_changes():
                print("Pushing due changes!")
                overlay_source_repo.git_push(commit_message=f"Updated {overlay.folder}!", push_untracked_files=True)

        if FileOp.dir_exists(repo_dir):
            overlays_repo_name = Statics.get_overlay_repo(android_version)
            overlays_repo_dir = Statics.get_overlay_directory(android_version)
            overlay_repo = Git(overlays_repo_dir)
            overlay_repo.clone_repo(overlays_repo_name, branch="master")
            for folder in Path(repo_dir).iterdir():
                if str(folder).endswith(".git"):
                    continue
                cmd = Cmd()
                overlay_path = cmd.build_overlay(folder_name=str(folder))
                if not overlay_path.__eq__(""):
                    print(f"{overlay_path} successfully built..")
                    print(
                        f"Copying to {os.path.join(overlays_repo_dir, str(Path(folder).name), f'{Path(folder).name}.apk')}")
                    FileOp.copy_file(overlay_path, os.path.join(overlays_repo_dir,
                                                                str(Path(folder).name), f"{Path(folder).name}.apk"))
                    folder_to_remove = os.path.join(str(folder), "dist")
                    FileOp.remove_dir(folder_to_remove)
                    folder_to_remove = os.path.join(str(folder), "build")
                    FileOp.remove_dir(folder_to_remove)
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
    overlay_control()
