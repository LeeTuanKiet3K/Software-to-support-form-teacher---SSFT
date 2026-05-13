'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  GraduationCap, Send, Sparkles, Bot, User,
  BookOpen, FileText, UserCheck, LogOut,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import type { ChatMessage } from '@/types';
import { mockChatHistory } from '@/lib/mockData';

// --- Mock AI response function ---
const QUICK_ACTIONS = [
  { label: 'Xem thủ tục', icon: FileText },
  { label: 'Hỏi về điểm', icon: BookOpen },
  { label: 'Gặp GVCN', icon: UserCheck },
];

function generateMockResponse(message: string): ChatMessage {
  const lower = message.toLowerCase();
  let content = '';
  let actions: string[] = [];

  if (lower.includes('bảo lưu') || lower.includes('bao luu')) {
    content = '📋 **Thủ tục bảo lưu học kỳ:**\n\n1. Điền đơn xin bảo lưu tại phòng Đào tạo (mẫu BL-01)\n2. Có chữ ký xác nhận của GVCN\n3. Nộp kèm minh chứng lý do (bệnh viện, gia đình...)\n4. Thời hạn nộp: **trước tuần 6** của học kỳ\n\nBạn có cần mình hỗ trợ thêm gì không ạ?';
    actions = ['Tải mẫu đơn BL-01', 'Liên hệ GVCN', 'Xem deadline'];
  } else if (lower.includes('điểm') || lower.includes('diem') || lower.includes('gpa')) {
    content = '📊 **Về điểm số và GPA:**\n\nĐiểm GPA được tính theo thang 4.0 dựa trên điểm chữ của từng môn.\n\n- A: 4.0 · B+: 3.5 · B: 3.0 · C+: 2.5 · C: 2.0 · D+: 1.5 · D: 1.0 · F: 0\n\nBạn muốn xem điểm môn nào hoặc cần tính GPA không ạ?';
    actions = ['Xem bảng điểm', 'Tính GPA', 'Đăng ký học lại'];
  } else if (lower.includes('học phí') || lower.includes('hoc phi') || lower.includes('tiền')) {
    content = '💰 **Thông tin học phí:**\n\nHọc phí được thu theo tín chỉ. Bạn có thể xem chi tiết và đóng học phí qua **Cổng thông tin sinh viên**.\n\n⚠️ Nếu bạn gặp khó khăn tài chính, nhà trường có chính sách hỗ trợ và vay vốn sinh viên. GVCN có thể hỗ trợ làm hồ sơ.';
    actions = ['Xem lịch đóng tiền', 'Hỗ trợ tài chính', 'Vay vốn sinh viên'];
  } else if (lower.includes('thẻ') || lower.includes('the sinh vien')) {
    content = '🪪 **Cấp lại thẻ sinh viên:**\n\n1. Nộp đơn tại **Phòng Công tác sinh viên** (Tầng 1, tòa A)\n2. Lệ phí: **50.000đ**\n3. Thời gian xử lý: **7 ngày làm việc**\n4. Mang theo CMND/CCCD khi nhận thẻ';
    actions = ['Tải mẫu đơn', 'Xem giờ làm việc', 'Bản đồ phòng ban'];
  } else {
    const responses = [
      'Mình đã ghi nhận câu hỏi của bạn. Vấn đề này cần được hỗ trợ kỹ hơn từ GVCN. Mình sẽ gửi thông báo đến thầy/cô ngay nhé!',
      'Cảm ơn bạn đã chia sẻ! Mình sẽ hỗ trợ bạn tốt nhất có thể. Bạn có thể mô tả chi tiết hơn về vấn đề không ạ?',
      'Mình hiểu rồi. Dựa trên thông tin bạn cung cấp, mình gợi ý bạn liên hệ trực tiếp phòng liên quan để được hỗ trợ nhanh nhất.',
    ];
    content = responses[Math.floor(Math.random() * responses.length)];
    actions = ['Liên hệ GVCN', 'Xem FAQ', 'Tìm phòng ban'];
  }

  return { role: 'assistant', content, timestamp: new Date().toISOString(), actions };
}

export default function StudentPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatHistory);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll xuống tin nhắn mới nhất
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || isTyping) return;

    // Thêm tin nhắn của user
    const userMsg: ChatMessage = { role: 'user', content: msg, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    // Giả lập AI đang gõ (1-2 giây)
    const delay = 1000 + Math.random() * 800;
    await new Promise((r) => setTimeout(r, delay));

    const aiMsg = generateMockResponse(msg);
    setMessages((prev) => [...prev, aiMsg]);
    setIsTyping(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen flex flex-col max-w-3xl mx-auto px-4">
      {/* --- Header --- */}
      <motion.header
        className="flex items-center justify-between py-4 border-b border-white/[0.06] sticky top-0 z-10
                   bg-navy-900/80 backdrop-blur-xl"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 to-blue-500
                          flex items-center justify-center shadow-glow-purple/30">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-white font-semibold text-sm">Trợ lý SSFT</p>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs text-slate-500">AI đang hoạt động</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => { sessionStorage.clear(); router.push('/login'); }}
          className="btn-ghost flex items-center gap-2 text-sm py-2"
        >
          <LogOut className="w-4 h-4" />
          Thoát
        </button>
      </motion.header>

      {/* --- Quick Action Chips --- */}
      <motion.div
        className="flex gap-2 py-3 overflow-x-auto scrollbar-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {QUICK_ACTIONS.map(({ label, icon: Icon }) => (
          <button
            key={label}
            onClick={() => handleSend(label)}
            className="flex items-center gap-2 px-4 py-2 rounded-full shrink-0
                       bg-navy-800/60 border border-white/[0.08] text-slate-300 text-sm
                       hover:bg-navy-700/60 hover:border-purple-500/30 hover:text-white
                       transition-all duration-200"
          >
            <Icon className="w-3.5 h-3.5 text-purple-400" />
            {label}
          </button>
        ))}
      </motion.div>

      {/* --- Message Area --- */}
      <div className="flex-1 space-y-5 py-4 overflow-y-auto">
        <AnimatePresence initial={false}>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1
                ${msg.role === 'user'
                  ? 'bg-purple-500/20 border border-purple-500/30'
                  : 'bg-blue-500/20 border border-blue-500/30'}`}>
                {msg.role === 'user'
                  ? <User className="w-4 h-4 text-purple-300" />
                  : <Bot className="w-4 h-4 text-blue-300" />}
              </div>

              {/* Bubble */}
              <div className={`max-w-[75%] space-y-2 ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                <div className={`px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap
                  ${msg.role === 'user' ? 'bubble-user' : 'bubble-ai'}`}>
                  {msg.content}
                </div>

                {/* Quick action tags */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {msg.actions.map((action, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(action)}
                        className="text-xs px-3 py-1.5 rounded-full
                                   bg-purple-500/10 border border-purple-500/20 text-purple-300
                                   hover:bg-purple-500/20 transition-colors duration-150"
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="flex gap-3"
            >
              <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30
                              flex items-center justify-center shrink-0">
                <Sparkles className="w-4 h-4 text-blue-300 animate-pulse" />
              </div>
              <div className="bubble-ai px-4 py-3">
                <div className="flex gap-1.5 items-center h-4">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={bottomRef} />
      </div>

      {/* --- Input Bar (sticky bottom) --- */}
      <motion.div
        className="sticky bottom-0 py-4 bg-navy-900/80 backdrop-blur-xl border-t border-white/[0.06]"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex gap-3 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi của bạn... (Enter để gửi)"
            rows={1}
            disabled={isTyping}
            className="input-dark flex-1 resize-none leading-relaxed max-h-32 overflow-y-auto
                       disabled:opacity-60 disabled:cursor-not-allowed"
            style={{ fieldSizing: 'content' } as React.CSSProperties}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isTyping}
            className="btn-primary p-3 shrink-0 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-slate-600 text-center mt-2">
          SSFT AI · Powered by Gemini + Llama 3 · Câu trả lời chỉ mang tính tham khảo
        </p>
      </motion.div>
    </div>
  );
}
