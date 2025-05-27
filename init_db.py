# init_db.py
from db import Base, engine
from models import ApprovalSheet, Author

Base.metadata.create_all(bind=engine)
