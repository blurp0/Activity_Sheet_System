# approval_db.py
from db import SessionLocal
from models import ApprovalSheet, Author
from datetime import datetime

def save_approval_sheet(title, authors, download_link, date_str=None):
    session = SessionLocal()
    try:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y").date() if date_str else None
        sheet = ApprovalSheet(
            title=title,
            download_link=download_link,
            date=date_obj
        )

        for name in authors:
            author = Author(name=name)
            sheet.authors.append(author)

        session.add(sheet)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error saving to DB: {e}")
        return False
    finally:
        session.close()


def delete_approval_sheet_by_download_link(download_link):
    session = SessionLocal()
    try:
        sheet = session.query(ApprovalSheet).filter(ApprovalSheet.download_link == download_link).first()
        if sheet:
            session.delete(sheet)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting from DB: {e}")
        return False
    finally:
        session.close()


def get_all_approval_sheets():
    session = SessionLocal()
    try:
        sheets = session.query(ApprovalSheet).all()
        results = []
        for sheet in sheets:
            results.append({
                'title': sheet.title,
                'authors': [author.name for author in sheet.authors],
                'date': sheet.date,
                'download_link': sheet.download_link,
                # add something identifying the file for deletion, e.g. filename or path
                'filename_or_path': extract_filename_from_url(sheet.download_link)
            })
        return results
    finally:
        session.close()

def extract_filename_from_url(url):
    # naive extraction from URL path, e.g. get last path segment
    return url.split('/')[-1]

