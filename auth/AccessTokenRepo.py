import os
from db.firestore import FIRESTORE as db

ACCESS_TOKEN = db.collection(
    "AccessToken" if os.getenv("PYTHON_ENV") == "prod" else "AccessToken-dev"
)
