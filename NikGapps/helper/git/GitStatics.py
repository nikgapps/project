from ..Statics import Statics


class GitStatics:
    tracker_repo_url = "git@github.com:nikgapps/tracker.git"
    tracker_repo_dir = Statics.cwd + Statics.dir_sep + "tracker"
    apk_source_repo = f"https://gitlab.com/nikgapps/"
    release_repo_url = "git@github.com:nikgapps/release.git"
    release_history_dir = Statics.cwd + Statics.dir_sep + "release"
    website_repo_url = "git@github.com:nikgapps/nikgapps.github.io.git"
    website_repo_dir = Statics.cwd + Statics.dir_sep + "nikgapps.github.io"
    config_repo_dir = Statics.cwd + Statics.dir_sep + "config"
    config_repo_url = "git@github.com:nikgapps/config.git"
