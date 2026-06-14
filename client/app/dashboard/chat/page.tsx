'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, User, FileText, Download, Mail } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  actions?: string[];
  dataTable?: {
    headers: string[];
    rows: string[][];
  };
}

export default function AdvisorChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'ai',
      content: 'Xin chào! Tôi là Trợ lý AI hỗ trợ Quản lý lớp học. Thầy/Cô cần tôi giúp phân tích điểm số, tóm tắt tình hình sinh viên hay tra cứu quy định nào ạ?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
    
    // Auto-fill prompt if provided in URL
    if (typeof window !== 'undefined' && messages.length === 1) {
      const params = new URLSearchParams(window.location.search);
      const promptParams = params.get('prompt');
      if (promptParams) {
        setInput(promptParams);
      }
    }
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await apiClient('/chat/advisor', {
        method: 'POST',
        body: JSON.stringify({ message: userMessage.content })
      });

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: response.content || 'Xin lỗi, tôi chưa hiểu ý cô.',
        actions: response.actions,
        dataTable: response.dataTable
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Lỗi khi gọi AI:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: 'Đã xảy ra lỗi khi kết nối với máy chủ AI. Vui lòng thử lại sau.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    setInput(action);
    // Có thể cho tự động gửi hoặc chờ người dùng bấm gửi
  };

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6 shrink-0">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shadow-glow-purple">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Trợ lý AI - Phân tích Học vụ</h1>
          <p className="text-sm text-slate-400">Kết nối trực tiếp với dữ liệu lớp học thời gian thực</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="glass-card flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 custom-scrollbar">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === 'ai' ? 'bg-purple-600/20 text-purple-400' : 'bg-blue-600/20 text-blue-400'
                }`}>
                  {msg.role === 'ai' ? <Sparkles className="w-4 h-4" /> : <User className="w-4 h-4" />}
                </div>

                {/* Content */}
                <div className={`space-y-3 ${msg.role === 'user' ? 'items-end' : ''}`}>
                  <div className={`px-4 py-3 text-sm rounded-2xl ${
                    msg.role === 'ai' 
                      ? 'bg-navy-800/80 border border-white/10 text-slate-200 rounded-tl-sm' 
                      : 'bg-gradient-to-br from-purple-600 to-blue-500 text-white rounded-tr-sm'
                  }`}>
                    {msg.content}
                  </div>

                  {/* Optional Data Table */}
                  {msg.dataTable && (
                    <div className="bg-navy-900 border border-white/10 rounded-xl overflow-hidden mt-2">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left whitespace-nowrap">
                          <thead className="bg-navy-950/50 text-slate-400 border-b border-white/5">
                            <tr>
                              {msg.dataTable.headers.map((h, i) => (
                                <th key={i} className="px-4 py-2 font-medium">{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-white/5 text-slate-300">
                            {msg.dataTable.rows.map((row, i) => (
                              <tr key={i} className="hover:bg-white/5">
                                {row.map((cell, j) => (
                                  <td key={j} className="px-4 py-2">
                                    {j === row.length - 1 ? (
                                      <span className="text-red-400 font-medium bg-red-500/10 px-2 py-0.5 rounded">{cell}</span>
                                    ) : cell}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Optional Quick Actions */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {msg.actions.map((act, i) => (
                        <button
                          key={i}
                          onClick={() => handleQuickAction(act)}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-purple-500/30 bg-purple-500/10 text-purple-300 text-xs hover:bg-purple-500/20 transition-colors"
                        >
                          {act.includes('Excel') ? <Download className="w-3.5 h-3.5" /> : 
                           act.includes('Email') ? <Mail className="w-3.5 h-3.5" /> : 
                           <FileText className="w-3.5 h-3.5" />}
                          {act}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-4 max-w-[85%]"
              >
                <div className="w-8 h-8 rounded-full bg-purple-600/20 text-purple-400 flex items-center justify-center shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div className="px-4 py-3 bg-navy-800/80 border border-white/10 rounded-2xl rounded-tl-sm flex items-center gap-1.5">
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-white/10 bg-navy-900/50">
          <form onSubmit={handleSend} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Hỏi AI về tình hình lớp, cảnh báo học vụ..."
              className="w-full bg-navy-950 border border-white/10 rounded-xl pl-4 pr-12 py-3.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-2 rounded-lg bg-purple-600 text-white disabled:opacity-50 disabled:bg-navy-800 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="flex gap-2 mt-3 overflow-x-auto custom-scrollbar pb-1">
            {['Lọc SV nguy cơ rớt môn', 'Điểm danh lớp', 'Thống kê khiếu nại'].map(hint => (
              <button
                key={hint}
                onClick={() => handleQuickAction(hint)}
                className="text-xs px-3 py-1.5 rounded-full border border-white/5 bg-white/5 text-slate-400 hover:text-white hover:bg-white/10 whitespace-nowrap transition-colors"
              >
                {hint}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}