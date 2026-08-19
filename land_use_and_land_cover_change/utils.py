import os

import git


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def print_section_heading(heading):
    print("______________________")
    print(heading)
    print("...")


def create_backgr_vars(nr_var, num_init):
    vars_list = ""
    for i in range(nr_var):
        num = i + num_init
        if len(str(num)) > 1:
            var_name = f"var8{num}"
        else:
            var_name = f"var80{num}"
        if i > 0:
            vars_list += "," + var_name
        else:
            vars_list += var_name
    return vars_list


def get_git_info_str(repo_path=None):
    """function extracts information about current git branch and hash of current commit"""
    git_info = {}

    # land-use-translator repository
    if repo_path is None:
        repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lut_repo = git.Repo(path=repo_path, search_parent_directories=True)
    try:
        git_info["lut"] = {
            "branch": lut_repo.active_branch.name,
            "commit": lut_repo.head.object.hexsha,
            "repo": lut_repo.remote().url.split("/")[-1].replace(".git", ""),
        }
    except TypeError:
        print("Current HEAD is detached. Store only current commit hash.")
        git_info["lut"] = {
            "branch": "Detached HEAD",
            "commit": lut_repo.head.object.hexsha,
            "repo": lut_repo.remote().url.split("/")[-1].replace(".git", ""),
        }

    git_info_str = f"Current land-use-translator git repository: {git_info['lut']['repo']}\n"
    git_info_str += f"Current land-use-translator git branch: {git_info['lut']['branch']}\n"
    git_info_str += f"Current land-use-translator git commit: {git_info['lut']['commit']}\n"

    return git_info_str


def get_repo_root() -> str:
    """
    Return the absolute path to the repository root.
    """
    # land-use-translator repository
    # use the path of the current file to get the path to the repository root
    repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lut_repo = git.Repo(path=repo_path, search_parent_directories=True)

    # Return the root from the repository
    return lut_repo.working_tree_dir
