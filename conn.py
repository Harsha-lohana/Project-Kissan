import firebase_admin
from firebase_admin import credentials, firestore

def connect_firebase():
    try:
        cred = credentials.Certificate("serviceAccountKey.json") #service key of firebase
        
        # Only initialize if not already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("✅ Connected to Firebase Firestore")
        return db

    except Exception as e:
        print("❌ Firebase connection error:", e)
        return None
