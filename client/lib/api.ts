const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = {
  // --- Auth ---
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Đăng nhập thất bại' }));
      throw new Error(err.detail || 'Lỗi kết nối máy chủ');
    }
    return res.json();
  },

  async logout(uid: string) {
    const res = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uid }),
    });
    return res.json();
  },

  // --- Issues ---
  async getPendingIssues() {
    const res = await fetch(`${API_BASE_URL}/issues/pending`, {
      method: 'GET',
    });
    if (!res.ok) throw new Error('Không thể lấy danh sách vấn đề');
    return res.json();
  },

  async updateIssueStatus(issueId: string, newStatus: string) {
    const res = await fetch(`${API_BASE_URL}/issues/${issueId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_status: newStatus }),
    });
    if (!res.ok) throw new Error('Không thể cập nhật trạng thái vấn đề');
    return res.json();
  },

  // --- Chat ---
  async sendChatMessage(chatId: string, studentId: string, studentMessage: string) {
    const res = await fetch(`${API_BASE_URL}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, student_id: studentId, student_message: studentMessage }),
    });
    if (!res.ok) throw new Error('Lỗi gửi tin nhắn');
    return res.json();
  },

  async getChatHistory(chatId: string) {
    const res = await fetch(`${API_BASE_URL}/chat/history/${chatId}`, {
      method: 'GET',
    });
    if (!res.ok) throw new Error('Không thể lấy lịch sử chat');
    return res.json();
  },
};
