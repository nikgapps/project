import time

from NikGapps.helper.git.Git import Git
import git.exc


class TestGit(Git):

    def git_push(self, commit_message=None, push_untracked_files=False, debug=False, rebase=True, pull_first=True, max_retries=3):
        if not self.enable_push:
            print("Git push is disabled, skipping push!")
            return False
        try:
            if pull_first:
                self.git_pull(rebase=rebase, max_retries=max_retries)

            if self.repo.is_dirty(untracked_files=True):
                self.repo.git.add(update=True)  # Update tracked files
                if push_untracked_files:
                    self.repo.git.add(all=True)  # Add all untracked files

                commit_message = commit_message or "Auto Commit"
                self.repo.index.commit(commit_message)
            return self.git_force_push(debug)

        except git.GitCommandError as e:
            print(f"Git command error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return False

    def git_pull(self, rebase=True, max_retries=3):
        origin = self.repo.remote(name='origin')
        origin.fetch()
        for retry in range(max_retries):
            try:
                if rebase:
                    self.repo.git.pull('--rebase')
                else:
                    self.repo.git.pull()
                break
            except git.GitCommandError as e:
                print(f"Error during pull/rebase: {e}, retrying...")
                time.sleep(10)  # Wait 10 seconds before retrying
        else:
            print("Max retries reached, pull/rebase failed.")
            return False
        return True

    def git_force_push(self, debug=False):
        origin = self.repo.remote(name='origin')
        push_info = origin.push(force=True)
        for info in push_info:
            if "rejected" in info.summary:
                print(info.summary)
                return False
            else:
                print("Pushed to origin.")
                if debug:
                    print(f"Pushed {info.summary}")
        return True
