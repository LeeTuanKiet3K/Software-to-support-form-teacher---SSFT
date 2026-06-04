'use client';

import { useState, useEffect, useRef } from 'react';
import { Send, User, Brain } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';
import type { IssueMessage } from '@/types';

interface IssueChatProps {
  issueId: string;
  currentUserId: string;
  currentUserRole: 'STUDENT' | 'ADVISOR';
}

export function IssueChat({ issueId, currentUserId, currentUserRole }: IssueChatProps) {
  const [messages, setMessages] = useState<IssueMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchMessages = async () => {
    try {
      const data = await apiClient(`/issues/${issueId}/messages`);
      if (Array.isArray(data)) {
        setMessages(data);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const markAsRead = async () => {
    try {
      await apiClient(`/issues/${issueId}/read`, {
        method: 'PATCH',
        body: JSON.stringify({ reader_role: currentUserRole })
      });
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  useEffect(() => {
    fetchMessages();
    markAsRead(); // Mark as read when opening the chat

    const interval = setInterval(() => {
      fetchMessages();
    }, 5000);

    return () => clearInterval(interval);
  }, [issueId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim() || isSending) return;
    
    setIsSending(true);
    const content = inputText.trim();
    setInputText('');
    
    // Optimistic UI update
    const tempMsg: IssueMessage = {
      message_id: Date.now().toString(),
      issue_id: issueId,
      sender_id: currentUserId,
      sender_role: currentUserRole,
      content: content,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMsg]);

    try {
      await apiClient(`/issues/${issueId}/messages`, {
        method: 'POST',
        body: JSON.stringify({
          sender_id: currentUserId,
          sender_role: currentUserRole,
          content: content
        })
      });
      // Fetch fresh to ensure we have the real ID and timestamp
      fetchMessages();
    } catch (error) {
      console.error('Error sending message:', error);
      // Remove optimistic message if failed
      setMessages(prev => prev.filter(m => m.message_id !== tempMsg.message_id));
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-[400px] border border-white/10 bg-navy-950/50 rounded-xl overflow-hidden mt-6">
      {/* Header */}
      <div className="bg-navy-900/80 border-b border-white/10 p-3 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
        <span className="text-sm font-medium text-slate-200">Trao đổi trực tiếp</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {isLoading && messages.length === 0 ? (
          <div className="text-center text-slate-500 text-sm mt-10">Đang tải tin nhắn...</div>
        ) : messages.length === 0 ? (
          <div className="text-center text-slate-500 text-sm mt-10">Chưa có tin nhắn nào. Bắt đầu cuộc trò chuyện ngay!</div>
        ) : (
          messages.map((msg) => {
            const isMine = msg.sender_role === currentUserRole;
            return (
              <div key={msg.message_id} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${isMine ? 'bg-purple-600 text-white rounded-br-none' : 'bg-navy-800 border border-white/5 text-slate-200 rounded-bl-none'}`}>
                  {!isMine && (
                    <div className="text-xs font-semibold mb-1 opacity-70">
                      {msg.sender_role === 'ADVISOR' ? 'Giáo viên chủ nhiệm' : 'Sinh viên'}
                    </div>
                  )}
                  {msg.content}
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 bg-navy-900/50 border-t border-white/10">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Nhập tin nhắn..."
            className="w-full bg-navy-950 border border-white/10 rounded-full pl-4 pr-12 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-purple-500/50 focus:ring-1 focus:ring-purple-500/50 placeholder-slate-500"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isSending}
            className="absolute right-1.5 p-2 rounded-full bg-purple-600 text-white hover:bg-purple-500 disabled:opacity-50 disabled:hover:bg-purple-600 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
