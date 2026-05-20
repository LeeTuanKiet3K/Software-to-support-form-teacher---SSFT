import time

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

    # =========================================================
    # TEST 1: SAVE DOCUMENT
    # =========================================================

    print("\n--- TEST 1: SAVE DOCUMENT ---")

    testData = {
        "tester": "HienDang",
        "message": "test successful",
        "test_time": time.time()
    }

    docId = db.saveDocument(
        "Test_Zone",
        testData,
        "test_2"
    )

    print(f"Document saved with ID: {docId}")

    time.sleep(1)

    # =========================================================
    # TEST 2: GET DOCUMENT
    # =========================================================

    print("\n--- TEST 2: GET DOCUMENT ---")

    readData = db.getDocument(
        "Test_Zone",
        docId
    )

    if readData:
        print("Document retrieved successfully!")
        print(f"Message: {readData['message']}")
        print(
            f"Created at: "
            f"{readData.get('created_at')}"
        )

    else:
        print("Document not found!")

    time.sleep(1)

    # =========================================================
    # TEST 3: LOG
    # =========================================================

    print("\n--- TEST 3: LOG ---")

    testIssue = {
        "student_id": "test_student",
        "content": "test issue",
        "status": "pending"
    }

    issueId = db.saveDocument(
        "Issues",
        testIssue
    )

    print(f"Issue saved with ID: {issueId}")
    print("Log saved successfully!")

    time.sleep(1)

    # =========================================================
    # TEST 4: UPDATE DOCUMENT
    # =========================================================

    print("\n--- TEST 4: UPDATE DOCUMENT ---")

    updateData = {
        "status": "resolved",
        "note": "Đã xử lý xong trong lúc test"
    }

    isUpdated = db.updateDocument(
        "Issues",
        issueId,
        updateData
    )

    if isUpdated:
        print(
            f"Issue [{issueId}] "
            f"updated successfully!"
        )

    else:
        print("Failed to update document!")

    time.sleep(1)

    # =========================================================
    # TEST 5: QUERY DOCUMENT
    # =========================================================

    print("\n--- TEST 5: QUERY DOCUMENT ---")

    filters = [
        ("tester", "==", "HienDang")
    ]

    results = db.queryDocuments(
        "Test_Zone",
        filters
    )

    if len(results) > 0:

        for item in results:

            print(
                f"Message = '{item.get('message')}' "
                f"| Tester = '{item.get('tester')}' "
                f"| Created At = {item.get('created_at')}"
            )

    else:
        print("No matching documents found!")

    time.sleep(1)

    # =========================================================
    # TEST 6: SAVE STORAGE
    # =========================================================

    print("\n--- TEST 6: SAVE STORAGE ---")

    imagePath = "test_image.png"

    try:

        with open(imagePath, "rb") as file:

            imageUrl = storage.uploadFile(
                fileData=file,
                fileName=imagePath,
                destinationFolder="avatars"
            )

        if imageUrl:

            print("File uploaded successfully!")
            print(f"Image URL: {imageUrl}")

        else:
            print("Failed to upload file!")

    except FileNotFoundError:
        print(
            f"Test image not found: {imagePath}"
        )
        return

    time.sleep(1)

    # =========================================================
    # TEST 7: DELETE STORAGE
    # =========================================================

    # print("\n--- TEST 7: DELETE STORAGE ---")

    # isDeleted = storage.deleteFile(imageUrl)

    # if isDeleted:
    #     print("File deleted successfully!")

    # else:
    #     print("Failed to delete file!")

    # time.sleep(1)



if __name__ == "__main__":
    run_test()