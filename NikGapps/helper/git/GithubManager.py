from github import Github


class GithubManager:

    def __init__(self, token):
        self.g = Github(token)
        self.user = self.g.get_user()

    def get_user(self):
        return self.g.get_user()

    def get_repos(self):
        return self.user.get_repos()

    def create_repo(self, repo_name):
        return self.user.create_repo(repo_name)

    @staticmethod
    def create_issue(repo, issue_title, issue_body):
        return repo.create_issue(title=issue_title, body=issue_body)
