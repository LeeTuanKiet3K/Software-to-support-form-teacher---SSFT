import os
from typing import List, Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env (Load environment variables)
load_dotenv()

class FirestoreHandler:
    """
    Lớp xử lý kết nối Firebase (Firebase Connection Manager) cho hệ thống hỗ trợ GVCN.
    """

    def __init__(self) -> None:
        """
        Khởi tạo dịch vụ (Initialize services) và kết nối tới database.
        """
        self.m_serviceAccountPath = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        
        if not self.m_serviceAccountPath:
            raise ValueError("Lỗi: FIREBASE_SERVICE_ACCOUNT_PATH không được tìm thấy trong tệp .env.")
        
        # Chỉ khởi tạo app nếu chưa tồn tại (Prevent multiple app initializations)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.m_serviceAccountPath)
            firebase_admin.initialize_app(cred)
        
        # Khởi tạo Firestore database client (Trình quản lý cơ sở dữ liệu)
        self.m_db = firestore.client()

    def verifyLogin(self, email: str, password: str) -> Optional[str]:
        """
        Xác thực người dùng (User Authentication).
        Kiểm tra thông tin đăng nhập trong collection 'Users'.
        
        Args:
            email (str): Địa chỉ email đăng nhập.
            password (str): Mật khẩu người dùng.
            
        Returns:
            Optional[str]: Trả về Role (Vai trò) của người dùng hoặc None nếu sai thông tin xác thực.
        """
        # Tham chiếu tới tập hợp người dùng (Reference to 'users' collection)
        usersRef = self.m_db.collection('Users')
        
        # Truy vấn tìm user theo email và giới hạn 1 kết quả (Optimize read operations)
        query = usersRef.where(filter=firestore.FieldFilter('email', '==', email)).limit(1).stream()
        
        for doc in query:
            userData = doc.to_dict()
            # So khớp mật khẩu đã lưu (Password verification)
            if userData.get('password') == password:
                return userData.get('role')  # Trả về Vai trò của user
                
        return None

    def getKnowledgeBase(self) -> List[Dict[str, any]]:
        """
        Lấy dữ liệu làm cơ sở tri thức (Fetch Knowledge Base) từ Firestore.
        Dữ liệu này dùng làm Grounding để tránh tình trạng AI bịa đặt (Hallucination fallback).
        
        Returns:
            List[Dict]: Danh sách các quy định và thông tin hỗ trợ từ hệ thống.
        """
        # Tham chiếu tới tập hợp Cơ sở tri thức (Reference to 'knowledge_base' collection)
        kbRef = self.m_db.collection('knowledge_base')
        
        # Tải toàn bộ tài liệu từ cơ sở tri thức (Fetch all documents)
        docs = kbRef.stream()
        
        knowledgeList = []
        for doc in docs:
            data = doc.to_dict()
            data['doc_id'] = doc.id
            knowledgeList.append(data)
            
        return knowledgeList
        
    def saveIssue(self, studentIdOrName: str, issueText: str, priorityLevel: str, status: str = "Pending Advisor") -> str:
        """
        Lưu vấn đề (Issue) của sinh viên vào Firestore khi cần sự can thiệp của GVCN.
        
        Args:
            studentIdOrName (str): Tên hoặc ID của sinh viên gửi vấn đề.
            issueText (str): Nội dung chi tiết của vấn đề.
            priorityLevel (str): Mức độ ưu tiên (vd: 'P0', 'P1').
            status (str): Trạng thái của vấn đề (mặc định là 'Pending Advisor' - Chờ GVCN xử lý).
            
        Returns:
            str: ID của document vừa được tạo.
        """
        # Tham chiếu tới tập hợp các vấn đề (Reference to 'issues' collection)
        issuesRef = self.m_db.collection('issues')
        
        # Dữ liệu cần lưu (Data to insert)
        issueData = {
            'student': studentIdOrName,
            'issue_text': issueText,
            'priority_level': priorityLevel,
            'status': status,
            'created_at': firestore.SERVER_TIMESTAMP  # Thời gian tạo do server Firebase tự định đoạt
        }
        
        # Thêm document (Add new document)
        updateTime, docRef = issuesRef.add(issueData)
        
        return docRef.id

    def getIssues(self) -> List[Dict[str, any]]:
        """
        Lấy danh sách các vấn đề (Issues) cần được Giáo viên xử lý,
        được sắp xếp theo mức độ ưu tiên: P0 > P1 > P2.
        
        Returns:
            List[Dict]: Danh sách vấn đề đã được sắp xếp.
        """
        issuesRef = self.m_db.collection('issues')
        # Lấy trạng thái Pending Advisor (Unresolved issues)
        query = issuesRef.where(filter=firestore.FieldFilter('status', '==', 'Pending Advisor')).stream()
        
        issuesList = []
        for doc in query:
            data = doc.to_dict()
            data['issue_id'] = doc.id
            issuesList.append(data)
            
        # Thuật toán sắp xếp ưu tiên (Priority Sorting Algorithm)
        # Gán trọng số: P0 = 0, P1 = 1, P2 = 2 (số càng nhỏ càng ưu tiên hiển thị trước)
        priorityWeight = {"P0": 0, "P1": 1, "P2": 2}
        
        # Sắp xếp danh sách dựa trên cột priority_level
        issuesList.sort(key=lambda x: priorityWeight.get(x.get('priority_level', 'P2'), 99))
        
        return issuesList

    def getUserProfile(self, uid: str) -> Optional[Dict[str, any]]:
        """
        Lấy thông tin hồ sơ người dùng ngay sau khi đăng nhập thành công.
        
        Args:
            uid (str): Document ID của người dùng.
            
        Returns:
            Optional[Dict]: Dữ liệu người dùng (nếu tồn tại), ngược lại trả về None.
        """
        userRef = self.m_db.collection('Users').document(uid)
        doc = userRef.get()
        if doc.exists:
            data = doc.to_dict()
            data['uid'] = doc.id
            return dict(data)
        return None

    def createUserProfile(self, uid: str, data: Dict[str, any]) -> bool:
        """
        Tạo mới hồ sơ người dùng (User Profile) trong cơ sở dữ liệu.
        
        Args:
            uid (str): Document ID dùng để lưu (thường là UID từ Firebase Auth hoặc tự sinh).
            data (Dict): Chứa các trường như 'full_name', 'email', 'role', vv.
                         Thời gian 'created_at' sẽ được tự động đính kèm.
        
        Returns:
            bool: Trạng thái tạo mới thành công.
        """
        userRef = self.m_db.collection('Users').document(uid)
        
        # Đính kèm thời gian khởi tạo (Append server timestamp)
        data['created_at'] = firestore.SERVER_TIMESTAMP
        
        try:
            userRef.set(data)
            return True
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
    def getDocument(self, collection: str, docId: str) -> Optional[Dict[str, any]]:
        """
        Lấy một document theo ID.

        Args:
            collection (str): Tên collection.
            docId (str): ID của document.

        Returns:
            Optional[Dict]: Dữ liệu document nếu tồn tại, ngược lại None.
        """
        docRef = self.m_db.collection(collection).document(docId)
        doc = docRef.get()

        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data

        return None

    def addDocument(self, collection: str, data: Dict[str, any]) -> str:
        """
        Thêm một document mới vào collection.

        Args:
            collection (str): Tên collection.
            data (Dict): Dữ liệu cần lưu.

        Returns:
            str: ID của document vừa tạo.
        """
        data["created_at"] = firestore.SERVER_TIMESTAMP

        _, docRef = self.m_db.collection(collection).add(data)

        return docRef.id

    def queryOne(self, collection: str, field: str, value: any) -> Optional[Dict[str, any]]:
        """
        Truy vấn lấy một document đầu tiên thỏa điều kiện.

        Args:
            collection (str): Tên collection.
            field (str): Tên field cần query.
            value (any): Giá trị so sánh.

        Returns:
            Optional[Dict]: Document đầu tiên nếu tìm thấy, ngược lại None.
        """
        query = self.m_db.collection(collection) \
            .where(filter=firestore.FieldFilter(field, "==", value)) \
            .limit(1) \
            .stream()

        for doc in query:
            data = doc.to_dict()
            data["id"] = doc.id
            return data

        return None

    def getClient(self):
        """
        Trả về Firestore client (dùng cho RealtimeHandler).

        Returns:
            firestore.Client: Firestore instance
        """
        return self.m_db