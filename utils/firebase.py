import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials from environment variable
firebase_creds = os.getenv("FIREBASE_CREDENTIALS_JSON")
if not firebase_creds:
    raise ValueError("Missing FIREBASE_CREDENTIALS_JSON environment variable.")

# Parse the JSON string and initialize Firebase
cred_dict = json.loads(firebase_creds)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()

def doc_exists(collection: str, doc_id: str) -> bool:
    """
    7. Validate Document Existence
    Checks if a document exists in a given collection.
    """
    if not doc_id:
        return False
    doc_ref = db.collection(collection).document(doc_id)
    return doc_ref.get().exists

print("✅ Firebase Initialized")
