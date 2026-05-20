'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, Send, Sparkles, User, Table as TableIcon, FileText, Calendar, ChevronRight 
} from 'lucide-react';

type AdminMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  dataTable?: { headers: string[]; rows: any[][] };
  actions?: string[];
};

const MOCK_CHAT: AdminMessage[] = [
  {
    id: '1',
    role: 'assistant',
    content: 'Chào cô Lan. Tôi là Trợ lý AI Hệ thống Hỗ trợ GVCN. Cô cần tôi tổng hợp báo cáo lớp, lọc danh sách sinh viên hay tư vấn hướng giải quyết vấn đề nào ạ?',
    actions: ['Lọc SV rớt môn', 'Thống kê điểm danh', 'Tạo thông báo lớp']
  }
];

export default function AdvisorChatPage() {
  const [messages, setMessages] = useState<AdminMessage[]>(MOCK_CHAT);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || isTyping) return;

    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: msg }]);
    setInput('');
    setIsTyping(true);

    // Simulate AI processing
    await new Promise(r => setTimeout(r, 1500));

    let response: AdminMessage = { id: Date.now().toString(), role: 'assistant', content: '' };

    if (msg.toLowerCase().includes('lọc')) {
      response.content = 'Dạ, đây là danh sách các sinh viên có nguy cơ bị cảnh báo học vụ dựa trên GPA kỳ trước và tỷ lệ điểm danh hiện tại:';
      response.dataTable = {
        headers: ['MSSV', 'Họ Tên', 'GPA', 'Điểm danh', 'Trạng thái'],
        rows: [
          ['24120101', 'Trần Quang Tuấn', '1.8', '65%', 'Nguy cơ cao'],
          ['24120102', 'Nguyễn Thị Bé', '2.0', '70%', 'Cần theo dõi'],
          ['24120103', 'Lê Văn Cường', '1.9', '80%', 'Cần theo dõi'],
        ]
      };
      response.actions = ['Xuất file Excel', 'Gửi Email nhắc nhở hàng loạt'];
    } else {
      response.content = 'Hệ thống đã ghi nhận yêu cầu của cô. Để thực hiện, cô có muốn tôi tự động soạn một bản nháp không?';
      response.actions = ['Soạn nháp', 'Xem dữ liệu thô'];
    }

    setMessages(prev => [...prev, response]);
    setIsTyping(false);
  };

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto px-6 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-1">Trợ lý AI Quản trị</h1>
        <p className="text-slate-400 text-sm">Hỗ trợ tra cứu dữ liệu, lên lịch và phân tích lớp học tự động</p>
      </div>

      {/* Chat Box */}
      <div className="flex-1 glass-card flex flex-col overflow-hidden relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar z-10">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-lg
                  ${msg.role === 'user' ? 'bg-gradient-to-br from-purple-500/40 to-blue-500/40 border border-purple-500/20' 
                                        : 'bg-navy-800 border border-white/10'}`}>
                  {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-purple-400" />}
                </div>

                <div className="space-y-3 min-w-0">
                  <div className={`px-5 py-3.5 text-sm leading-relaxed rounded-2xl
                    ${msg.role === 'user' ? 'bg-purple-600 text-white rounded-tr-sm' 
                                          : 'bg-navy-800/80 border border-white/5 text-slate-200 rounded-tl-sm'}`}>
                    {msg.content}
                  </div>

                  {/* Render Data Table if exists */}
                  {msg.dataTable && (
                    <div className="bg-navy-900/50 border border-white/10 rounded-xl overflow-hidden mt-2">
                      <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border-b border-white/5">
                        <TableIcon className="w-4 h-4 text-purple-400" />
                        <span className="text-xs font-semibold text-slate-300">Dữ liệu phân tích</span>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm whitespace-nowrap">
                          <thead className="bg-navy-800/30 text-slate-400">
                            <tr>
                              {msg.dataTable.headers.map((h, i) => (
                                <th key={i} className="px-4 py-3 font-medium">{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-white/5">
                            {msg.dataTable.rows.map((row, i) => (
                              <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                                {row.map((cell, j) => (
                                  <td key={j} className={`px-4 py-3 ${j === 0 ? 'text-white font-medium' : 'text-slate-300'}
                                                          ${cell === 'Nguy cơ cao' ? 'text-red-400' : ''}`}>
                                    {cell}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  {msg.actions && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {msg.actions.map((act, i) => (
                        <button key={i} onClick={() => handleSend(act)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-300
                                     hover:bg-purple-500/20 hover:border-purple-500/30 hover:text-purple-300 transition-all">
                          {act}
                          <ChevronRight className="w-3 h-3 opacity-50" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}

            {isTyping && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 max-w-[85%]">
                <div className="w-10 h-10 rounded-2xl bg-navy-800 border border-white/10 flex items-center justify-center shrink-0">
                  <Sparkles className="w-5 h-5 text-purple-400 animate-pulse" />
                </div>
                <div className="bg-navy-800/80 border border-white/5 rounded-2xl rounded-tl-sm px-5 py-4 flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" />
                  <div className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '0.15s' }} />
                  <div className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '0.3s' }} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="p-4 bg-navy-900/50 border-t border-white/5 z-10">
          <div className="relative flex items-end gap-2 bg-navy-950 border border-white/10 rounded-2xl p-2 focus-within:border-purple-500/50 focus-within:ring-1 focus-within:ring-purple-500/50 transition-all">
            <button className="p-3 text-slate-500 hover:text-purple-400 transition-colors">
              <FileText className="w-5 h-5" />
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
              placeholder="Nhập lệnh hoặc câu hỏi cho AI... (Ví dụ: Lọc danh sách rớt môn)"
              className="flex-1 max-h-32 bg-transparent text-white placeholder-slate-500 text-sm py-3 px-2 resize-none focus:outline-none custom-scrollbar"
              rows={1}
              disabled={isTyping}
            />
            <button 
              onClick={() => handleSend()}
              disabled={!input.trim() || isTyping}
              className="p-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-xl transition-colors shrink-0"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
