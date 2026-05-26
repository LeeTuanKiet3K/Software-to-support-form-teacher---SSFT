import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.FirebaseAuthHandler import FirebaseAuthHandler
from app.services.FirestoreHandler import FirestoreHandler
from app.core.Constants import UserRole

def create_advisor_account(email, password, name):
    auth_handler = FirebaseAuthHandler()
    db_handler = FirestoreHandler()

    uid = auth_handler.createAuthUser(email, password)
    if not uid:
        print("Failed to create auth user.")
        return

    profileData = {
        "email": email,
        "full_name": name,
        "role": UserRole.ADVISOR,
        "requires_password_change": False,
        "is_active": True,
        "avatar_url": "",
    }
    
    success = db_handler.createUserProfile(uid, profileData)
    if success:
        print(f"Successfully created advisor account!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    else:
        print("Failed to create Firestore profile.")

if __name__ == "__main__":
    create_advisor_account("admin@hcmus.edu.vn", "12345678", "Admin Teacher")
