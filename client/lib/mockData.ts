// Các hằng số hiển thị giao diện (UI Display Helpers)

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
