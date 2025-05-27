from flask import Flask, render_template, request, redirect, url_for, flash
from github import Github
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', '')

# GitHub configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO = os.environ.get('GITHUB_REPO', '')  # Format: "owner/repo"

print(app.secret_key)
print(GITHUB_TOKEN)
print(GITHUB_REPO)

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

def delete_pdf_from_github(filename):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        raise Exception("GitHub token or repository not configured.")

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)

    path_in_repo = f"{APPROVAL_SHEET_FOLDER}/{os.path.basename(filename)}"
    existing_file = repo.get_contents(path_in_repo)
    repo.delete_file(path_in_repo, f"Delete {filename}", existing_file.sha)

@app.route("/", methods=["GET", "POST"])
def index():
    selected_pdf_url = ""
    if request.method == "POST":
        if 'upload_pdf' in request.form:
            upload_file = request.files.get('pdf_file')
            request_title = request.form.get('request_title', '').strip()
            filename = upload_file.filename if upload_file else ''

            if not request_title:
                flash("Request title is required.", "error")
            elif not upload_file or filename == '':
                flash("No PDF file selected for upload.", "error")
            elif not filename.lower().endswith('.pdf'):
                flash("Filename must end with .pdf extension.", "error")
            else:
                try:
                    push_pdf_to_github(upload_file.read(), filename, request_title)
                    clean_folder = sanitize_folder_name(request_title)
                    flash(f"Successfully uploaded and pushed {filename} to GitHub.", "success")
                    selected_pdf_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{APPROVAL_SHEET_FOLDER}/{clean_folder}/{filename}"
                except Exception as e:
                    flash(f"Failed to push file to GitHub: {e}", "error")

        elif 'delete_pdf' in request.form:
            filename = request.form.get("filename", "").strip()
            if not filename:
                flash("Filename to delete is required.", "error")
            else:
                try:
                    delete_pdf_from_github(filename)
                    flash(f"Successfully deleted {filename} from GitHub.", "success")
                except Exception as e:
                    flash(f"Failed to delete {filename}: {e}", "error")

        else:
            selected_pdf_url = request.form.get("pdf_url", "").strip()
            if selected_pdf_url and not selected_pdf_url.lower().endswith(".pdf"):
                flash("Selected URL does not point to a PDF file.", "error")
                selected_pdf_url = ""

    pdf_files = get_pdf_files_from_repo()

    return render_template("index.html", pdf_files=pdf_files, selected_pdf_url=selected_pdf_url)

if __name__ == "__main__":
    app.run(debug=True)
