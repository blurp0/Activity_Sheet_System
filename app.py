from flask import Flask, render_template, request, redirect, url_for, flash
from github import Github
import os
import re
from app_utils import (
    APPROVAL_SHEET_FOLDER, GITHUB_REPO, GITHUB_TOKEN,
    delete_pdf_from_github, push_pdf_to_github, sanitize_folder_name
)
from db_functions import (
    delete_approval_sheet_by_download_link,
    save_approval_sheet,
    get_all_approval_sheets
)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', '')

print(app.secret_key)
print(GITHUB_TOKEN)
print(GITHUB_REPO)

@app.route("/", methods=["GET", "POST"])
def index():
    selected_pdf_url = ""
    if request.method == "POST":
        if 'upload_pdf' in request.form:
            upload_file = request.files.get('pdf_file')
            request_title = request.form.get('request_title', '').strip()
            filename = upload_file.filename if upload_file else ''
            authors_raw = request.form.get('authors', '').strip()
            date_str = request.form.get('date', '').strip()  # Expected format: MM/DD/YY

            if not request_title:
                flash("Request title is required.", "error")
            elif not upload_file or filename == '':
                flash("No PDF file selected for upload.", "error")
            elif not filename.lower().endswith('.pdf'):
                flash("Filename must end with .pdf extension.", "error")
            else:
                try:
                    # Push to GitHub
                    push_pdf_to_github(upload_file.read(), filename, request_title)

                    # Correct download URL based on sanitized folder
                    clean_folder = sanitize_folder_name(request_title)
                    selected_pdf_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{APPROVAL_SHEET_FOLDER}/{clean_folder}/{filename}"

                    flash(f"Successfully uploaded", "success")

                    # Save metadata to DB
                    authors = [a.strip() for a in authors_raw.split(",") if a.strip()]
                    saved = save_approval_sheet(
                        title=request_title,
                        authors=authors,
                        download_link=selected_pdf_url,
                        date_str=date_str
                    )
                    if saved:
                        flash("Metadata saved to database.", "success")
                    else:
                        flash("Failed to save metadata to database.", "error")

                except Exception as e:
                    flash(f"Failed to push file to GitHub: {e}", "error")


        elif 'delete_pdf' in request.form:
            download_link = request.form.get("download_link", "").strip()
            title = request.form.get("title", "").strip()
            if not download_link or not title:
                flash("Download link and title are required to delete.", "error")
            else:
                try:
                    delete_pdf_from_github(download_link)
                    deleted = delete_approval_sheet_by_download_link(download_link)
                    if deleted:
                        flash(f"Successfully deleted", "success")
                    else:
                        flash(f"Deleted file from GitHub, but failed to delete metadata from database.", "warning")
                except Exception as e:
                    flash(f"Failed to delete '{title}': {e}", "error")



        else:
            selected_pdf_url = request.form.get("pdf_url", "").strip()
            if selected_pdf_url and not selected_pdf_url.lower().endswith(".pdf"):
                flash("Selected URL does not point to a PDF file.", "error")
                selected_pdf_url = ""

    # Load approval sheets metadata from DB for listing
    approval_sheets = get_all_approval_sheets()

    return render_template(
        "index.html",
        approval_sheets=approval_sheets,
        selected_pdf_url=selected_pdf_url
    )


if __name__ == "__main__":
    app.run(debug=True)
