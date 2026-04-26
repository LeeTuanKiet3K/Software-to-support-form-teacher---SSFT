import time
import io
from app.services.FirestoreHandler import FirestoreHandler
from app.services.StorageHandler import StorageHandler

def run_test():
    try:
        db = FirestoreHandler()
        storage = StorageHandler()
        print("Connected to database successfully!")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    print("\n--- TEST 1: SAVE DOCUMENT ---")
    test_data = {
        "tester": "HienDang",
        "message": "test successful",
        "test_time": time.time()
    }

    doc_id = db.saveDocument("Test_Zone", test_data, "test_2")
    print(f"Document saved with ID: {doc_id}")
    time.sleep(1)


    print("\n--- TEST 2: GET DOCUMENT ---")
    read_data = db.getDocument("Test_Zone", doc_id)
    if read_data:
        print(f"Document retrieved successfully! Content: {read_data['message']}")
        print(f"Auto-generated timestamp: created_at = {read_data.get('created_at')}")
    else:
        print("Document not found!")
    time.sleep(1)


    print("--- TEST 3: LOG ---")

    test_issue = {
        "student_id": "test",
        "content": "test issue",
        "status": "pending"
    }
    issue_id = db.saveDocument("Issues", test_issue)
    print(f"Document saved with ID: {issue_id}")
    print("log saved\n")
    time.sleep(1)


    print("--- TEST 4: UPDATE DOCUMENT ---")
    update_data = {
        "status": "resolved", 
        "note": "Đã xử lý xong trong lúc test"
    }
    is_updated = db.updateDocument("Issues", issue_id, update_data)
    if is_updated:
        print(f"Document updated successfully! Issue [{issue_id}] is now resolved.")
    else:
        print("Failed to update document")
    print("\n")
    time.sleep(1)


    print("--- TEST 5: QUERY  ---")
    filters = [("tester", "==", "Hien")]
    results = db.queryDocuments("Test_Zone", filters)
    if len(results) > 0:
        print(f"Document: message = '{results[0].get('message')}' | tester = '{results[0].get('tester')}' | created_at = {results[0].get('created_at')}")
    print("\n")
    time.sleep(1)


if __name__ == "__main__":
    run_test()