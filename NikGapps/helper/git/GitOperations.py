import json
from ..FileOp import FileOp
from .Git import Git
from .GitStatics import GitStatics
from ..Statics import Statics


class GitOperations:

    @staticmethod
    def setup_tracker_repo(fresh_clone=True):
        return GitOperations.setup_repo(GitStatics.tracker_repo_dir, GitStatics.tracker_repo_url, "main", fresh_clone)

    @staticmethod
    def setup_repo(repo_dir, repo_url, branch="main", fresh_clone=True, commit_depth=50):
        print()
        print("Repo Dir: " + repo_dir)
        repo = Git(repo_dir)
        result = repo.clone_repo(repo_url, branch=branch, fresh_clone=fresh_clone, commit_depth=commit_depth)
        return repo if result else None

    @staticmethod
    def clone_overlay_repo(android_version, fresh_clone=False, branch="master"):
        if float(android_version) > 12:
            android_code = Statics.get_android_code(android_version)
            overlay_source_dir = Statics.cwd + Statics.dir_sep + f"overlays_{android_code}"
            overlay_source_repo = f"https://github.com/nikgapps/overlays_{android_code}.git"
            return GitOperations.setup_repo(overlay_source_dir, overlay_source_repo, branch, fresh_clone)
        else:
            print(f"Cloning Overlay repo not needed for android {android_version}")
            return None

    @staticmethod
    def clone_apk_repo(android_version, arch="arm64", fresh_clone=False, branch="main"):
        arch = "" if arch == "arm64" else "_" + arch
        apk_source_directory = Statics.cwd + Statics.dir_sep + str(android_version) + arch
        apk_source_repo = GitStatics.apk_source_repo + str(android_version) + arch + ".git"
        return GitOperations.setup_repo(apk_source_directory, apk_source_repo, branch, fresh_clone, commit_depth=1)

    @staticmethod
    def get_last_commit_date(branch, repo_dir=Statics.cwd, repo_url=None, android_version=None):
        last_commit_datetime = None
        if android_version is not None:
            repository = GitOperations.clone_apk_repo(android_version, branch=branch)
        else:
            repository = Git(repo_dir)
            if repo_url is not None:
                repository.clone_repo(repo_url=repo_url, fresh_clone=False, branch=branch)
        if repository is not None:
            last_commit_datetime = repository.get_latest_commit_date(branch=branch)
        return last_commit_datetime

    @staticmethod
    def get_release_repo(release_type):
        release_repo = Git(GitStatics.release_history_dir)
        if not FileOp.dir_exists(GitStatics.release_history_dir):
            if release_type == "canary":
                GitStatics.release_repo_url = "git@github.com:nikgapps/canary-release.git"
            release_repo.clone_repo(GitStatics.release_repo_url, branch="master", commit_depth=50)
            if not FileOp.dir_exists(GitStatics.release_history_dir):
                print(GitStatics.release_history_dir + " doesn't exist!")
        return release_repo

    @staticmethod
    def get_website_repo_for_changelog(repo_dir=GitStatics.website_repo_dir, repo_url=GitStatics.website_repo_url,
                                       branch="master"):
        repo = Git(repo_dir)
        if repo_url is not None:
            repo.clone_repo(repo_url=repo_url, fresh_clone=False, branch=branch)
        if not FileOp.dir_exists(GitStatics.website_repo_dir):
            print(f"Repo {repo_dir} doesn't exist!")
        return repo

    @staticmethod
    def mark_a_release(android_version, release_type):
        tracker_repo = GitOperations.setup_tracker_repo(False)
        if tracker_repo is not None:
            release_tracker = tracker_repo.working_tree_dir + Statics.dir_sep + "release_tracker.json"
            decoded_hand = {}
            if FileOp.file_exists(release_tracker):
                with open(release_tracker, "r") as file:
                    decoded_hand = json.load(file)
                if release_type not in decoded_hand:
                    decoded_hand[release_type] = {}
                decoded_hand[release_type][android_version] = Statics.time
            else:
                decoded_hand[release_type] = {}
                decoded_hand[release_type][android_version] = Statics.time
            print(f"Marking a release with {decoded_hand}")
            with open(release_tracker, "w") as file:
                json.dump(decoded_hand, file, indent=2, sort_keys=True)
            if tracker_repo.due_changes():
                tracker_repo.git_push(
                    f"Updated release_tracker.json with latest {release_type} release date: " + Statics.time)
            else:
                print("No changes to commit!")
