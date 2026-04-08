import os
from typing import List, Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env (Load environment variables)
load_dotenv()

class FirebaseHandler:
    """
    Lớp xử lý kết nối Firebase (Firebase Connection Manager) cho hệ thống hỗ trợ GVCN.
    """

    def __init__(self) -> None:
        """
        Khởi tạo dịch vụ (Initialize services) và kết nối tới database.
        """
        self.service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        
        if not self.service_account_path:
            raise ValueError("Lỗi: FIREBASE_SERVICE_ACCOUNT_PATH không được tìm thấy trong tệp .env.")
        
        # Chỉ khởi tạo app nếu chưa tồn tại (Prevent multiple app initializations)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.service_account_path)
            firebase_admin.initialize_app(cred)
        
        # Khởi tạo Firestore database client (Trình quản lý cơ sở dữ liệu)
        self.db = firestore.client()

    def verify_login(self, email: str, password: str) -> Optional[str]:
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
        users_ref = self.db.collection('Users')
        
        # Truy vấn tìm user theo email và giới hạn 1 kết quả (Optimize read operations)
        query = users_ref.where(filter=firestore.FieldFilter('email', '==', email)).limit(1).stream()
        
        for doc in query:
            user_data = doc.to_dict()
            # So khớp mật khẩu đã lưu (Password verification)
            if user_data.get('password') == password:
                return user_data.get('role')  # Trả về Vai trò của user
                
        return None

    def get_knowledge_base(self) -> List[Dict[str, any]]:
        """
        Lấy dữ liệu làm cơ sở tri thức (Fetch Knowledge Base) từ Firestore.
        Dữ liệu này dùng làm Grounding để tránh tình trạng AI bịa đặt (Hallucination fallback).
        
        Returns:
            List[Dict]: Danh sách các quy định và thông tin hỗ trợ từ hệ thống.
        """
        # Tham chiếu tới tập hợp Cơ sở tri thức (Reference to 'knowledge_base' collection)
        kb_ref = self.db.collection('knowledge_base')
        
        # Tải toàn bộ tài liệu từ cơ sở tri thức (Fetch all documents)
        docs = kb_ref.stream()
        
        knowledge_list = []
        for doc in docs:
            data = doc.to_dict()
            data['doc_id'] = doc.id
            knowledge_list.append(data)
            
        return knowledge_list
        
    def save_issue(self, student_id_or_name: str, issue_text: str, priority_level: str, status: str = "Pending Advisor") -> str:
        """
        Lưu vấn đề (Issue) của sinh viên vào Firestore khi cần sự can thiệp của GVCN.
        
        Args:
            student_id_or_name (str): Tên hoặc ID của sinh viên gửi vấn đề.
            issue_text (str): Nội dung chi tiết của vấn đề.
            priority_level (str): Mức độ ưu tiên (vd: 'P0', 'P1').
            status (str): Trạng thái của vấn đề (mặc định là 'Pending Advisor' - Chờ GVCN xử lý).
            
        Returns:
            str: ID của document vừa được tạo.
        """
        # Tham chiếu tới tập hợp các vấn đề (Reference to 'issues' collection)
        issues_ref = self.db.collection('issues')
        
        # Dữ liệu cần lưu (Data to insert)
        issue_data = {
            'student': student_id_or_name,
            'issue_text': issue_text,
            'priority_level': priority_level,
            'status': status,
            'created_at': firestore.SERVER_TIMESTAMP  # Thời gian tạo do server Firebase tự định đoạt
        }
        
        # Thêm document (Add new document)
        update_time, doc_ref = issues_ref.add(issue_data)
        
        return doc_ref.id

    def get_issues(self) -> List[Dict[str, any]]:
        """
        Lấy danh sách các vấn đề (Issues) cần được Giáo viên xử lý,
        được sắp xếp theo mức độ ưu tiên: P0 > P1 > P2.
        
        Returns:
            List[Dict]: Danh sách vấn đề đã được sắp xếp.
        """
        issues_ref = self.db.collection('issues')
        # Lấy trạng thái Pending Advisor (Unresolved issues)
        query = issues_ref.where(filter=firestore.FieldFilter('status', '==', 'Pending Advisor')).stream()
        
        issues_list = []
        for doc in query:
            data = doc.to_dict()
            data['issue_id'] = doc.id
            issues_list.append(data)
            
        # Thuật toán sắp xếp ưu tiên (Priority Sorting Algorithm)
        # Gán trọng số: P0 = 0, P1 = 1, P2 = 2 (số càng nhỏ càng ưu tiên hiển thị trước)
        priority_weight = {"P0": 0, "P1": 1, "P2": 2}
        
        # Sắp xếp danh sách dựa trên cột priority_level
        issues_list.sort(key=lambda x: priority_weight.get(x.get('priority_level', 'P2'), 99))
        
        return issues_list

    def get_user_profile(self, uid: str) -> Optional[Dict[str, any]]:
        """
        Lấy thông tin hồ sơ người dùng ngay sau khi đăng nhập thành công.
        
        Args:
            uid (str): Document ID của người dùng.
            
        Returns:
            Optional[Dict]: Dữ liệu người dùng (nếu tồn tại), ngược lại trả về None.
        """
        user_ref = self.db.collection('Users').document(uid)
        doc = user_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['uid'] = doc.id
            return dict(data)
        return None

    def create_user_profile(self, uid: str, data: Dict[str, any]) -> bool:
        """
        Tạo mới hồ sơ người dùng (User Profile) trong cơ sở dữ liệu.
        
        Args:
            uid (str): Document ID dùng để lưu (thường là UID từ Firebase Auth hoặc tự sinh).
            data (Dict): Chứa các trường như 'full_name', 'email', 'role', vv.
                         Thời gian 'created_at' sẽ được tự động đính kèm.
        
        Returns:
            bool: Trạng thái tạo mới thành công.
        """
        user_ref = self.db.collection('Users').document(uid)
        
        # Đính kèm thời gian khởi tạo (Append server timestamp)
        data['created_at'] = firestore.SERVER_TIMESTAMP
        
        try:
            user_ref.set(data)
            return True
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
