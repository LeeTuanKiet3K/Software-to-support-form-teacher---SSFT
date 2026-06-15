import sys
import os
import random
from datetime import datetime, timedelta

# Đảm bảo in ra tiếng Việt không bị lỗi trên Windows Terminal
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.FirebaseAuthHandler import FirebaseAuthHandler
from app.services.FirestoreHandler import FirestoreHandler
from app.core.Constants import UserRole
from firebase_admin import firestore, auth as admin_auth

FIRST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MIDDLE_NAMES = ["Thị", "Văn", "Ngọc", "Minh", "Hữu", "Đức", "Hoàng", "Thanh", "Quang", "Xuân", "Gia", "Tuấn", "Thành", "Đình", "Hài"]
LAST_NAMES = ["Anh", "Bảo", "Chi", "Duy", "Giang", "Hà", "Hải", "Khang", "Linh", "Mai", "Nam", "Nga", "Phát", "Quyên", "Sơn", "Trang", "Tuấn", "Vy", "Yến", "Thảo", "Huy", "Kha", "Tài", "Đạt", "Lộc"]

def generate_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(LAST_NAMES)}"

def delete_existing_data(db_handler, class_id, advisor_email):
    print(f"\n--- ĐANG DỌN DẸP DỮ LIỆU CŨ LỚP {class_id} & GVCN {advisor_email} ---")
    
    # 1. Xóa trong Users
    users_ref = db_handler.m_db.collection("Users")
    docs = users_ref.where(filter=firestore.FieldFilter("class_id", "==", class_id)).stream()
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
    print(f" Đã xóa {count} tài khoản học sinh trong Users.")
    
    # Xóa tài khoản giáo viên chủ nhiệm cũ
    advisor_docs = users_ref.where(filter=firestore.FieldFilter("email", "==", advisor_email)).stream()
    for doc in advisor_docs:
        doc.reference.delete()
        print(f" Đã xóa hồ sơ cũ của giáo viên {advisor_email}")

    # 2. Xóa trong Academic_records
    records_ref = db_handler.m_db.collection("Academic_records")
    docs = records_ref.where(filter=firestore.FieldFilter("class_id", "==", class_id)).stream()
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
    print(f" Đã xóa {count} bảng điểm trong Academic_records.")

    # 3. Xóa trong Issues
    issues_ref = db_handler.m_db.collection("Issues")
    docs = issues_ref.where(filter=firestore.FieldFilter("class_id", "==", class_id)).stream()
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
    print(f" Đã xóa {count} vấn đề trong Issues.")
    
    # 4. Xóa trong Notifications
    notif_ref = db_handler.m_db.collection("Notifications")
    docs = notif_ref.where(filter=firestore.FieldFilter("class_id", "==", class_id)).stream()
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
    print(f" Đã xóa {count} thông báo trong Notifications.")

def seed_perfect_data():
    auth_handler = FirebaseAuthHandler()
    db_handler = FirestoreHandler()

    advisor_email = "nguyentanminh@hcmus.edu.vn"
    advisor_password = "Password123"
    advisor_name = "Nguyễn Tấn Minh"
    advisor_class = "24CTT2"

    # Dọn dẹp dữ liệu cũ trước khi nạp mới
    delete_existing_data(db_handler, advisor_class, advisor_email)

    print("\n--- BẮT ĐẦU NẠP DỮ LIỆU MỚI TOÀN DIỆN ---")
    
    # 1. TẠO TÀI KHOẢN GIÁO VIÊN CHỦ NHIỆM
    print(f"\nĐang tạo Auth cho GVCN: {advisor_email}")
    advisor_uid = auth_handler.createAuthUser(advisor_email, advisor_password)
    
    # Nếu tài khoản Auth đã tồn tại sẵn, truy vấn ngược để lấy UID thực tế
    if not advisor_uid:
        print(" Tài khoản Auth đã tồn tại. Đang tìm UID thực tế...")
        try:
            user_rec = admin_auth.get_user_by_email(advisor_email)
            advisor_uid = user_rec.uid
            print(f"=> Tìm thấy UID thực tế: {advisor_uid}")
        except Exception as err:
            print(f" Lỗi truy vấn Auth: {err}. Sử dụng fallback 'hotantruong_hcmus'")
            advisor_uid = "hotantruong_hcmus"
        
    advisor_profile = {
        "email": advisor_email,
        "full_name": advisor_name,
        "role": UserRole.ADVISOR,
        "class_id": advisor_class,
        "requires_password_change": False,
        "is_active": True,
        "avatar_url": "",
    }
    db_handler.createUserProfile(advisor_uid, advisor_profile)
    print("=> Nạp hồ sơ GVCN thành công.")

    # 2. TẠO 40 SINH VIÊN
    print("\n--- ĐANG TẠO 40 TÀI KHOẢN SINH VIÊN VÀ BẢNG ĐIỂM ---")
    student_password = "Password123"
    students_list = []

    random_suffixes = sorted(random.sample(range(1, 1000), 40))
    for idx, suffix in enumerate(random_suffixes):
        mssv = f"24120{suffix:03d}"
        student_email = f"{mssv}@student.hcmus.edu.vn"
        student_name = generate_random_name()
        
        print(f"[{idx + 1}/40] {mssv} - {student_name}")
        
        # Tạo Auth User
        uid = auth_handler.createAuthUser(student_email, student_password)
        if not uid:
            # Nếu auth trùng, lấy UID thực từ Firebase Auth
            try:
                user_rec = admin_auth.get_user_by_email(student_email)
                uid = user_rec.uid
            except Exception:
                uid = f"uid_student_{mssv}"
            
        # Ghi profile vào Users
        student_profile = {
            "email": student_email,
            "full_name": student_name,
            "role": UserRole.STUDENT,
            "student_id": mssv,
            "class_id": advisor_class,
            "requires_password_change": False,
            "is_active": True,
            "avatar_url": "",
        }
        db_handler.createUserProfile(uid, student_profile)
        students_list.append({"uid": uid, "mssv": mssv, "name": student_name})

        # Ghi bảng điểm vào Academic_records (Document ID là MSSV)
        gpa = round(random.uniform(4.0, 9.5), 2)
        grades_data = {
            "student_id": uid,
            "class_id": advisor_class,
            "gpa": gpa,
            "is_low_score": gpa < 5.0,
            "ai_check_sent": False,
            "subjects": [
                {"subject_name": "Nhập môn Lập trình", "score": round(random.uniform(3.0, 10.0), 1)},
                {"subject_name": "Toán rời rạc", "score": round(random.uniform(3.0, 10.0), 1)},
                {"subject_name": "Cơ sở dữ liệu", "score": round(random.uniform(3.0, 10.0), 1)},
                {"subject_name": "Kỹ năng mềm", "score": round(random.uniform(5.0, 10.0), 1)}
            ],
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        db_handler.saveDocument("Academic_records", grades_data, documentId=mssv)

    # 3. TẠO DỮ LIỆU ISSUES VÀ NOTIFICATIONS CHO SINH VIÊN
    print("\n--- ĐANG TẠO VẤN ĐỀ (ISSUES) VÀ THÔNG BÁO CHO TỪNG SINH VIÊN ---")
    intents = ["tam_ly", "khieu_nai", "hoi_dap", "khac"]
    priorities = ["URGENT", "HIGH", "MEDIUM", "LOW"]
    statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "PENDING_ADVISOR"]
    
    issue_titles = [
        "Căng thẳng trầm cảm do áp lực học tập",
        "Xin phúc khảo điểm thi môn Cơ sở dữ liệu",
        "Hỏi về chính sách học bổng khuyến khích học tập",
        "Hệ thống đăng ký môn học Portal bị lỗi",
        "Làm đơn xin tạm dừng học kỳ vì lý do sức khỏe",
        "Khủng hoảng tâm lý do gia đình gặp biến cố",
        "Thủ tục xin cấp lại thẻ sinh viên bị mất",
        "Làm đơn xin gia hạn thời gian nộp học phí",
        "Cần tư vấn về quy trình chuyển ngành học",
        "Mâu thuẫn nội bộ khi làm bài tập lớn nhóm"
    ]

    # Tạo khoảng 20 issues ngẫu nhiên phân bổ cho các sinh viên
    for i in range(20):
        student = random.choice(students_list)
        intent = random.choice(intents)
        priority = random.choice(priorities)
        status = random.choice(statuses)
        title = random.choice(issue_titles)
        
        days_ago = random.randint(1, 20)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        issue_data = {
            "student_id": student["mssv"],
            "class_id": advisor_class,
            "intent": intent,
            "sentiment": "Tiêu cực" if priority in ["URGENT", "HIGH"] else "Bình thường",
            "priority": priority,
            "status": status,
            "is_advisor_viewed": status == "RESOLVED",
            "title": title,
            "category": "Học tập" if intent in ["hoi_dap", "khac"] else "Tâm lý",
            "content": f"Em chào thầy, hiện tại em gặp vấn đề: {title}. Em rất lo lắng và mong nhận được sự hỗ trợ từ thầy.",
            "created_at": created_at,
            "updated_at": created_at
        }
        
        # Lưu vào collection Issues
        db_handler.saveDocument("Issues", issue_data)
        
        # Đồng thời tạo thông báo ảo trong collection Notifications gửi cho sinh viên tương ứng
        notif_data = {
            "user_id": student["mssv"],
            "class_id": advisor_class,
            "title": "Cập nhật yêu cầu hỗ trợ",
            "content": f"Yêu cầu '{title}' của bạn đã chuyển sang trạng thái {status}.",
            "type": "system",
            "is_read": False,
            "created_at": created_at
        }
        db_handler.saveDocument("Notifications", notif_data)

    print("\n--- HOÀN THÀNH TẠO DỮ LIỆU THỬ NGHIỆM HỆ THỐNG ---")
    print(f"Đăng nhập GVCN: {advisor_email} | Password: {advisor_password}")
    print(f"Đăng nhập Sinh viên mẫu: {students_list[0]['mssv']}@student.hcmus.edu.vn | Password: {student_password}")

if __name__ == "__main__":
    seed_perfect_data()
