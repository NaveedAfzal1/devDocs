import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
# Note: Ensure your serviceAccountKey.json is secure and not exposed.
cred = credentials.Certificate("firebase/serviceAccountKey.json")
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
