import os

from google.cloud import firestore

db = firestore.Client()
DB = db.collection(
    f"EcommerceService{'-dev' if os.getenv('PYTHON_ENV', 'dev') == 'dev' else ''}"
)
