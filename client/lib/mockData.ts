// Mock Data — Dữ liệu giả để test UI trước khi kết nối API thật
import type {
  Issue, KpiStats, ChatMessage, BarChartData, PieChartData,
  AcademicRecord, Notification, User,
} from '@/types';

// --- Người dùng mẫu (Mock Users) ---
export const mockAdvisor: User = {
  uid: 'advisor_001',
  full_name: 'ThS. Nguyễn Thị Lan',
  email: 'lan.gvcn@hcmus.edu.vn',
  role: 'advisor',
  class_id: '24CTT4',
  is_active: true,
  avatar_url: undefined,
};

export const mockStudent: User = {
  uid: 'student_001',
  full_name: 'Nguyễn Văn An',
  email: 'an.sv@hcmus.edu.vn',
  role: 'student',
  class_id: '24CTT4',
  student_id: '24127001',
  is_active: true,
};

// --- KPI Thống kê (Dashboard Cards) ---
export const mockKpiStats: KpiStats = {
  urgent: 3,
  pending: 8,
  resolved: 24,
  totalStudents: 42,
};

// --- Danh sách vấn đề (Issues List) ---
export const mockIssues: Issue[] = [
  {
    id: 'ISS001',
    student_id: 'Nguyễn Văn An',
    chat_id: 'chat_an_001',
    intent: 'tam_ly',
    sentiment: 'tieu_cuc',
    priority: 'URGENT',
    status: 'OPEN',
    is_advisor_viewed: false,
    created_at: '2026-05-12T10:15:00Z',
  },
  {
    id: 'ISS002',
    student_id: 'Trần Thị Bảo',
    chat_id: 'chat_bao_001',
    intent: 'khieu_nai',
    sentiment: 'tieu_cuc',
    priority: 'HIGH',
    status: 'OPEN',
    is_advisor_viewed: false,
    created_at: '2026-05-12T09:30:00Z',
  },
  {
    id: 'ISS003',
    student_id: 'Lê Hoàng Cường',
    chat_id: 'chat_cuong_001',
    intent: 'hoi_dap',
    sentiment: 'trung_lap',
    priority: 'MEDIUM',
    status: 'IN_PROGRESS',
    is_advisor_viewed: true,
    created_at: '2026-05-11T14:00:00Z',
  },
  {
    id: 'ISS004',
    student_id: 'Phạm Minh Đức',
    chat_id: 'chat_duc_001',
    intent: 'khieu_nai',
    sentiment: 'tieu_cuc',
    priority: 'HIGH',
    status: 'OPEN',
    is_advisor_viewed: false,
    created_at: '2026-05-11T08:45:00Z',
  },
  {
    id: 'ISS005',
    student_id: 'Võ Thị Em',
    chat_id: 'chat_em_001',
    intent: 'hoi_dap',
    sentiment: 'tich_cuc',
    priority: 'LOW',
    status: 'RESOLVED',
    is_advisor_viewed: true,
    created_at: '2026-05-10T16:20:00Z',
  },
  {
    id: 'ISS006',
    student_id: 'Đỗ Văn Phúc',
    chat_id: 'chat_phuc_001',
    intent: 'tam_ly',
    sentiment: 'tieu_cuc',
    priority: 'URGENT',
    status: 'PENDING_ADVISOR',
    is_advisor_viewed: false,
    created_at: '2026-05-12T07:00:00Z',
  },
];

// --- Lịch sử Chat mẫu (Chat History for Student) ---
export const mockChatHistory: ChatMessage[] = [
  {
    role: 'assistant',
    content: 'Xin chào! Mình là trợ lý AI của Hệ thống Hỗ trợ GVCN. Mình có thể giúp bạn giải đáp thắc mắc, hướng dẫn thủ tục, hoặc kết nối với GVCN khi cần. Bạn đang cần hỗ trợ gì ạ? 😊',
    timestamp: '2026-05-12T10:00:00Z',
    actions: ['Xem thủ tục', 'Hỏi về điểm', 'Gặp GVCN'],
  },
];

// --- Dữ liệu biểu đồ (Chart Data) ---
export const mockPieData: PieChartData[] = [
  { name: 'Tâm lý', value: 12, color: '#ef4444' },
  { name: 'Khiếu nại', value: 18, color: '#f59e0b' },
  { name: 'Hỏi đáp', value: 35, color: '#3b82f6' },
  { name: 'Khác', value: 7, color: '#94a3b8' },
];

export const mockBarData: BarChartData[] = [
  { week: 'Tuần 1', urgent: 2, high: 4, medium: 8, low: 5 },
  { week: 'Tuần 2', urgent: 1, high: 6, medium: 10, low: 3 },
  { week: 'Tuần 3', urgent: 4, high: 3, medium: 7, low: 6 },
  { week: 'Tuần 4', urgent: 3, high: 5, medium: 9, low: 4 },
];

// --- Bảng điểm mẫu (Academic Records) ---
export const mockAcademicRecord: AcademicRecord = {
  student_id: 'student_001',
  class_id: '24CTT4',
  gpa: 2.85,
  subjects: [
    { subject_name: 'Toán cao cấp', score: 6.5 },
    { subject_name: 'Lập trình Python', score: 8.0 },
    { subject_name: 'CSDL', score: 7.5 },
    { subject_name: 'Mạng máy tính', score: 5.0 },
    { subject_name: 'Vật lý đại cương', score: 4.5 },
  ],
  is_low_score: false,
  ai_check_sent: false,
  updated_at: '2026-05-10T00:00:00Z',
};

// --- Thông báo mẫu (Notifications) ---
export const mockNotifications: Notification[] = [
  {
    id: 'NOTIF001',
    user_id: 'advisor_001',
    title: 'Cảnh báo học vụ',
    content: 'Sinh viên Nguyễn Văn An có GPA giảm mạnh xuống 1.8.',
    type: 'system',
    is_read: false,
    created_at: '2026-05-12T08:00:00Z',
  },
  {
    id: 'NOTIF002',
    user_id: 'advisor_001',
    title: 'Vấn đề khẩn cấp mới',
    content: 'Sinh viên Đỗ Văn Phúc cần hỗ trợ tâm lý khẩn cấp.',
    type: 'issue',
    is_read: false,
    created_at: '2026-05-12T07:05:00Z',
  },
];

// --- Labels tiếng Việt (UI Display Helpers) ---
export const PRIORITY_LABELS: Record<string, string> = {
  URGENT: 'Khẩn cấp',
  HIGH: 'Ưu tiên cao',
  MEDIUM: 'Trung bình',
  LOW: 'Thấp',
};

export const STATUS_LABELS: Record<string, string> = {
  OPEN: 'Chờ xử lý',
  IN_PROGRESS: 'Đang xử lý',
  RESOLVED: 'Đã giải quyết',
  PENDING_ADVISOR: 'Chờ GVCN',
};

export const INTENT_LABELS: Record<string, string> = {
  tam_ly: 'Tâm lý',
  khieu_nai: 'Khiếu nại',
  hoi_dap: 'Hỏi đáp',
  khong_ro: 'Không rõ',
};

export const SENTIMENT_LABELS: Record<string, string> = {
  tieu_cuc: 'Tiêu cực',
  tich_cuc: 'Tích cực',
  trung_lap: 'Trung lập',
};
