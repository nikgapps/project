from ..FileOp import FileOp
from .Git import Git
from .GitStatics import GitStatics
from ..Statics import Statics


class GitOperations:

    @staticmethod
    def setup_tracker_repo(fresh_clone=True):
        print()
        print("Repo Dir: " + GitStatics.tracker_repo_dir)
        tracker_repo = Git(GitStatics.tracker_repo_dir)
        result = tracker_repo.clone_repo(GitStatics.tracker_repo_url, fresh_clone=fresh_clone)
        return tracker_repo if result else None

    @staticmethod
    def clone_overlay_repo(android_version, fresh_clone=False, branch="master"):
        android_code = Statics.get_android_code(android_version)
        overlay_source_dir = Statics.pwd + Statics.dir_sep + f"overlays_{android_code}"
        overlay_source_repo = f"git@github.com:nikgapps/overlays_{android_code}.git"
        repository = Git(overlay_source_dir)
        result = repository.clone_repo(repo_url=overlay_source_repo, fresh_clone=fresh_clone, branch=branch)
        return repository if result else None

    @staticmethod
    def clone_apk_repo(android_version, fresh_clone=False, branch="main"):
        apk_source_directory = Statics.pwd + Statics.dir_sep + str(android_version)
        apk_source_repo = GitStatics.apk_source_repo + str(android_version) + ".git"
        repository = Git(apk_source_directory)
        result = repository.clone_repo(repo_url=apk_source_repo, fresh_clone=fresh_clone, branch=branch)
        return repository if result else None

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
