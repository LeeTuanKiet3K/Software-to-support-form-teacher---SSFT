// Types (Kiểu dữ liệu) dùng chung toàn bộ frontend Hệ thống Hỗ trợ GVCN

export type UserRole = 'student' | 'advisor' | 'admin';

export interface User {
  uid: string;
  full_name: string;
  email: string;
  role: UserRole;
  class_id: string;
  student_id?: string;
  avatar_url?: string;
  is_active: boolean;
}

// Mức độ ưu tiên vấn đề (Issue Priority)
export type IssuePriority = 'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW';

// Trạng thái vấn đề (Issue Status)
export type IssueStatus = 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'PENDING_ADVISOR';

// Ý định của sinh viên (Intent từ Llama3)
export type IssueIntent = 'tam_ly' | 'khieu_nai' | 'hoi_dap' | 'khong_ro';

// Cảm xúc (Sentiment từ Llama3)
export type IssueSentiment = 'tich_cuc' | 'tieu_cuc' | 'trung_lap';

export interface Issue {
  id: string;
  student_id: string;       // Tên hoặc UID sinh viên
  chat_id?: string;
  intent: IssueIntent;
  sentiment: IssueSentiment;
  priority: IssuePriority;
  status: IssueStatus;
  is_advisor_viewed: boolean;
  unread_by_advisor?: number;
  unread_by_student?: number;
  created_at: string;
  updated_at?: string;
  title?: string;
  category?: string;
  content?: string;
}

// Tin nhắn chat (Chat Message)
export type MessageRole = 'user' | 'assistant';

export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp?: string;
  actions?: string[];       // Quick action tags
}

export interface IssueMessage {
  message_id: string;
  issue_id: string;
  sender_id: string;
  sender_role: 'STUDENT' | 'ADVISOR';
  content: string;
  created_at?: string;
}

// KPI thống kê (Key Performance Indicators)
export interface KpiStats {
  urgent: number;
  pending: number;
  resolved: number;
  totalStudents: number;
}

// Dữ liệu biểu đồ (Chart Data)
export interface PieChartData {
  name: string;
  value: number;
  color: string;
}

export interface BarChartData {
  week: string;
  urgent: number;
  high: number;
  medium: number;
  low: number;
}

// Kết quả học tập (Academic Record)
export interface SubjectScore {
  subject_name: string;
  score: number;
}

export interface AcademicRecord {
  student_id: string;
  class_id: string;
  subjects: SubjectScore[];
  gpa: number;
  is_low_score?: boolean;
  ai_check_sent?: boolean;
  updated_at?: string;
}

// Thông báo (Notification)
export interface Notification {
  id: string;
  user_id: string;
  title: string;
  content: string;
  type: 'issue' | 'system' | 'announcement';
  is_read: boolean;
  created_at: string;
}

// Auth
export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthState {
  isLoggedIn: boolean;
  user: User | null;
  role: UserRole | null;
}
