import os
from db.firestore import DB

ACCESS_TOKEN = DB.collection(
    "AccessToken" if os.getenv("PYTHON_ENV") == "prod" else "AccessToken-dev"
)
