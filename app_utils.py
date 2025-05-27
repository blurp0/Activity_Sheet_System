import re
from github import Github
import os
from urllib.parse import unquote

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO = os.environ.get('GITHUB_REPO', '')  # Format: "owner/repo"
APPROVAL_SHEET_FOLDER = "Approval Sheet"

def sanitize_folder_name(name):
    name = re.sub(r'[^\w\s-]', '', name)  # Remove unsafe characters
    name = re.sub(r'\s+', '_', name.strip())  # Replace spaces with underscores
    return name

def get_pdf_files_from_repo():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return []

    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        default_branch = repo.default_branch
        base_folder = APPROVAL_SHEET_FOLDER

        pdf_files = []

        # Get all folders in the approval sheet directory
        top_contents = repo.get_contents(base_folder)

        for item in top_contents:
            if item.type == "dir":
                folder_name = item.name
                folder_path = f"{base_folder}/{folder_name}"
                sub_contents = repo.get_contents(folder_path)

                for file in sub_contents:
                    if file.type == "file" and file.name.lower().endswith(".pdf"):
                        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{default_branch}/{folder_path}/{file.name}"
                        pdf_files.append({"title": folder_name, "url": raw_url})
                        break  # Assumes one PDF per folder

        return pdf_files

    except Exception as e:
        print(f"Error fetching PDFs from repo: {e}")
        return []


def push_pdf_to_github(file_bytes, filename, request_title):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        raise Exception("GitHub token or repository not configured.")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)

    clean_filename = os.path.basename(filename)
    clean_folder = sanitize_folder_name(request_title)
    path_in_repo = f"{APPROVAL_SHEET_FOLDER}/{clean_folder}/{clean_filename}"

    try:
        existing_file = repo.get_contents(path_in_repo)
        repo.update_file(path_in_repo, f"Update {clean_filename}", file_bytes, existing_file.sha)
    except Exception:
        repo.create_file(path_in_repo, f"Add {clean_filename}", file_bytes)

def delete_pdf_from_github(download_link):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        raise Exception("GitHub token or repository not configured.")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    try:
        parts = download_link.split(f"/{GITHUB_REPO}/main/")
        if len(parts) != 2:
            raise Exception("Download link does not contain expected repository path.")
        path_in_repo = unquote(parts[1])

        existing_file = repo.get_contents(path_in_repo)
        repo.delete_file(path_in_repo, f"Delete {path_in_repo}", existing_file.sha)
    except Exception as e:
        raise Exception(f"Error deleting file from GitHub: {e}")

