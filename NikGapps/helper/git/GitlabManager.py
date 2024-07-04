import math
import shutil
import time
from pathlib import Path

import gitlab

from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.Statics import Statics
from NikGapps.helper.git.GitOperations import GitOperations


class GitLabManager:
    def __init__(self, gitlab_url='https://gitlab.com', private_token=None):
        self.token = private_token
        self.gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        self.gl.auth()

    def fetch_user_details(self, user_id):
        """Fetches user details for a specified user ID."""
        user = self.gl.users.get(user_id)
        return user

    def create_repository(self, project_name):
        """Creates a new repository with the given project name."""
        project = self.gl.projects.create({'name': project_name})
        return project

    def provide_owner_access(self, project_id, user_id):
        """Provides owner access to a repository for a particular user."""
        project = self.gl.projects.get(project_id)
        member = project.members.create({
            'user_id': user_id,
            'access_level': 50
        })
        return member

    def get_project(self, project_name):
        # Fetch all projects for the current user
        projects = self.gl.projects.list(owned=True, all=True)

        # Print details of each project
        for project in projects:
            if project.name == project_name:
                return project
        return None

    def create_and_commit_readme(self, project_id, branch_name="main", content="# Welcome to your new project"):
        """Creates a README.md file and commits it to the specified repository."""
        project = self.gl.projects.get(project_id)
        commit_data = {
            'branch': branch_name,
            'commit_message': 'Add README.md',
            'actions': [
                {
                    'action': 'create',
                    'file_path': 'README.md',
                    'content': content
                }
            ]
        }
        commit = project.commits.create(commit_data)
        return commit

    def create_and_commit_file(self, project_id, branch_name="main", file_path="file.txt", content=""):
        """Creates a file and commits it to the specified repository."""
        project = self.gl.projects.get(project_id)
        commit_data = {
            'branch': branch_name,
            'commit_message': f'Add {file_path}',
            'actions': [
                {
                    'action': 'create',
                    'file_path': file_path,
                    'content': content
                }
            ]
        }
        commit = project.commits.create(commit_data)
        return commit

    def create_gitlab_repository(self, project_name, visibility='public'):
        try:
            project = self.gl.projects.create({'name': project_name, 'visibility': visibility})
            return project.web_url
        except Exception as e:
            raise Exception(f"Failed to create GitLab repository: {e}")

    def get_repository_users_with_access_levels(self, project_id):
        access_levels = {
            10: 'Guest',
            20: 'Reporter',
            30: 'Developer',
            40: 'Maintainer',
            50: 'Owner'
        }

        project = self.gl.projects.get(project_id)
        members = project.members.list(all=True)
        user_access_levels = [(member.username, member.access_level, access_levels.get(member.access_level, 'Unknown'))
                              for member in
                              members]

        return user_access_levels

    def list_projects_with_ids(self, print_details=False):
        namespace_name = "nikgapps"
        # Fetch all projects for the current user
        projects = self.gl.projects.list(owned=True, all=True)

        # Print details of each project
        for project in projects:
            if not print_details:
                return projects
            project_details = self.gl.projects.get(project.id, statistics=True)
            storage_size = math.ceil(project_details.statistics["storage_size"] / (1024 ** 2) * 100) / 100
            print(f'Project Name: {project.name}, Project ID: {project.id}, Namespace: {project.namespace["path"]}, '
                  f'Storage Size: {storage_size} MB')
        return projects

    def find_project_allocated_size(self, repo_name):
        project = self.get_project(repo_name)
        project_details = self.gl.projects.get(project.id, statistics=True)
        return math.ceil(project_details.statistics["storage_size"] / (1024 ** 2) * 100) / 100

    def delete_project(self, project_id):
        try:
            project = self.gl.projects.get(project_id)
            project.delete()
            print(f"Project {project_id} deleted successfully.")
        except Exception as e:
            print(f"Failed to delete project {project_id}: {e}")

    def reset_repository(self, repo_name, gitattributes=None, user_id=8064473, sleep_for=10, delete_only=False):
        try:
            print(f"Resetting repository {repo_name}...")
            project = self.get_project(repo_name)
            self.delete_project(project.id)
            if not delete_only:
                print("Waiting for 10 seconds for the project to be completely deleted...")
                time.sleep(sleep_for)
                project = self.create_repository(repo_name)
                self.provide_owner_access(project_id=project.id, user_id=user_id)
                self.create_and_commit_readme(project_id=project.id)
                if gitattributes is not None:
                    commit = self.create_and_commit_file(project_id=project.id, file_path=".gitattributes",
                                                         content=gitattributes)
                    print(commit)
            return project
        except Exception as e:
            print(f"Failed to reset repository: {e}")
            return None

    def reset_repository_storage(self, repo_name, user_id=8064473, sleep_for=10, storage_cap=9000):
        project = self.get_project(repo_name)
        project_details = self.gl.projects.get(project.id, statistics=True)
        storage_size = math.ceil(project_details.statistics["storage_size"] / (1024 ** 2) * 100) / 100
        if storage_size > storage_cap:
            print(f"Storage size of {storage_size} MB exceeds the limit of {storage_cap} MB "
                  f"for project id {project.id}. Resetting...")
            old_repo_dir = Statics.pwd + Statics.dir_sep + f"{repo_name}_old"
            old_repo = GitOperations.setup_repo(repo_dir=f"{old_repo_dir}", repo_url=project_details.ssh_url_to_repo)
            project = self.reset_repository(repo_name, user_id=user_id, sleep_for=sleep_for)
            new_repo_dir = Statics.pwd + Statics.dir_sep + f"{repo_name}_new"
            new_repo = GitOperations.setup_repo(repo_dir=f"{new_repo_dir}", repo_url=project_details.ssh_url_to_repo)
            for item in Path(old_repo.working_tree_dir).rglob('*'):
                if '.git' in item.parts:
                    continue
                destination = Path(new_repo.working_tree_dir) / item.relative_to(Path(old_repo.working_tree_dir))
                if item.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    print(f"Copying {item} to {destination}")
                    shutil.copy2(item, destination)
            new_repo.git_push("Initial Commit", push_untracked_files=True)
            project_details = self.gl.projects.get(project.id, statistics=True)
            storage_size = math.ceil(project_details.statistics["storage_size"] / (1024 ** 2) * 100) / 100
            print(f"Repository storage for project id {project.id} reset successfully. "
                  f"New storage size: {storage_size} MB")
            FileOp.remove_dir(old_repo.working_tree_dir)
            FileOp.remove_dir(new_repo.working_tree_dir)

        else:
            print(f"Storage size of {storage_size} MB is within the limit of {storage_cap} MB. No action required.")

    def copy_repository(self, source_repo_name, target_repo_name, user_id=8064473):
        project = self.get_project(source_repo_name)
        old_repo_dir = Statics.pwd + Statics.dir_sep + f"{source_repo_name}_old"
        old_repo = GitOperations.setup_repo(repo_dir=f"{old_repo_dir}", repo_url=project.ssh_url_to_repo)
        if self.get_project(target_repo_name) is not None:
            print(f"Project {target_repo_name} already exists. Exiting...")
            return
        project = self.create_repository(target_repo_name)
        self.provide_owner_access(project_id=project.id, user_id=user_id)
        self.create_and_commit_readme(project_id=project.id)
        new_repo_dir = Statics.pwd + Statics.dir_sep + f"{target_repo_name}_new"
        new_repo = GitOperations.setup_repo(repo_dir=f"{new_repo_dir}", repo_url=project.ssh_url_to_repo)
        for item in Path(old_repo.working_tree_dir).rglob('*'):
            if '.git' in item.parts:
                continue
            destination = Path(new_repo.working_tree_dir) / item.relative_to(Path(old_repo.working_tree_dir))
            if item.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                print(f"Copying {item} to {destination}")
                shutil.copy2(item, destination)
        new_repo.git_push("Initial Commit", push_untracked_files=True)
