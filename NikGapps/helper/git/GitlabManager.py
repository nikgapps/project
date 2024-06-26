import math
import time

import gitlab


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

    def get_project_id(self, project_name):
        # Fetch all projects for the current user
        projects = self.gl.projects.list(owned=True, all=True)

        # Print details of each project
        for project in projects:
            if project.name == project_name:
                return project.id
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
        gl = gitlab.Gitlab("https://gitlab.com", private_token=self.token)
        namespace_name = "nikgapps"
        project_full_path = f"{namespace_name}/apkmirror"
        # Fetch the current user's details to get their ID
        user = gl.user

        # Fetch all projects for the current user
        projects = gl.projects.list(owned=True, all=True)

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
        project_id = self.get_project_id(repo_name)
        project_details = self.gl.projects.get(project_id, statistics=True)
        return math.ceil(project_details.statistics["storage_size"] / (1024 ** 2) * 100) / 100

    def delete_project(self, project_id):
        try:
            project = self.gl.projects.get(project_id)
            project.delete()
            print(f"Project {project_id} deleted successfully.")
        except Exception as e:
            print(f"Failed to delete project {project_id}: {e}")

    def reset_apk_repository(self, repo_name, message="""*.apk filter=lfs diff=lfs merge=lfs -text
            *.so filter=lfs diff=lfs merge=lfs -text
            """, user_id=8064473, sleep_for=10, delete_only=False):
        try:
            print(f"Resetting repository {repo_name}...")
            project_id = self.get_project_id(repo_name)
            self.delete_project(project_id)
            if not delete_only:
                print("Waiting for 10 seconds for the project to be completely deleted...")
                time.sleep(sleep_for)
                project = self.create_repository(repo_name)
                self.provide_owner_access(project_id=project.id,
                                          user_id=user_id)
                self.create_and_commit_readme(project_id=project.id)
                commit = self.create_and_commit_file(project_id=project.id, file_path=".gitattributes",
                                                     content=message)
                print(commit)
        except Exception as e:
            print(f"Failed to reset repository: {e}")
