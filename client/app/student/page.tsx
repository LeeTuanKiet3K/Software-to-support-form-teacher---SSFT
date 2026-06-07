'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GraduationCap, Send, Sparkles, Bot, User, BookOpen, FileText, UserCheck, LogOut, MessageSquare, AlertCircle, CheckCircle2, RefreshCw, Key, X, Eye, EyeOff, Bell, AlertTriangle, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/apiClient';
import { IssueTable } from '@/components/IssueTable';
import type { Issue } from '@/types';

type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  actions?: string[];
};

type TabType = 'ai' | 'form' | 'grades' | 'my-issues';

type GradeRecord = {
  subject_name: string;
  score: number;
};

type AcademicRecord = {
  gpa: number;
  subjects: GradeRecord[];
  updated_at?: string;
};

const QUICK_ACTIONS = [
  { label: 'Quy định của trường', icon: FileText },
  { label: 'Tư vấn học tập', icon: BookOpen },
  { label: 'Liên lạc GVCN', icon: UserCheck },
];

export default function StudentPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('ai');

  // AI Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Form State
  const [formTitle, setFormTitle] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formLoading, setFormLoading] = useState(false);
  const [formSuccess, setFormSuccess] = useState('');
  const [formError, setFormError] = useState('');

  // Grades State
  const [grades, setGrades] = useState<AcademicRecord | null>(null);
  const [gradesLoading, setGradesLoading] = useState(false);

  // My Issues State
  const [myIssues, setMyIssues] = useState<Issue[]>([]);
  const [issuesLoading, setIssuesLoading] = useState(false);

  // Password Modal State
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Get student ID from session
  const studentId = typeof window !== 'undefined' ? sessionStorage.getItem('ssft_id') || '24120101' : '24120101';
  const studentUid = typeof window !== 'undefined' ? sessionStorage.getItem('ssft_uid') || sessionStorage.getItem('ssft_id') || '24120101' : '24120101';
  const studentName = typeof window !== 'undefined' ? sessionStorage.getItem('ssft_name') || 'Sinh viên' : 'Sinh viên';

  // Notifications State
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotif, setShowNotif] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = async () => {
    try {
      const data = await apiClient(`/notifications/student/${studentId}`);
      if (data && data.notifications) {
        setNotifications(data.notifications);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleMarkAsRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient(`/notifications/${id}/read`, { method: 'PUT' });
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteNotification = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient(`/notifications/${id}`, { method: 'DELETE' });
      setNotifications(prev => prev.filter(n => n.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('action') === 'change-password') {
        setShowPasswordModal(true);
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotif(false);
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (activeTab === 'ai') {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping, activeTab]);

  useEffect(() => {
    if (activeTab === 'grades' && !grades) {
      fetchGrades();
    }
    
    let interval: NodeJS.Timeout;
    if (activeTab === 'my-issues') {
      fetchMyIssues();
      interval = setInterval(fetchMyIssues, 10000); // Tự động cập nhật mỗi 10 giây
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeTab]);

  const fetchMyIssues = async () => {
    setIssuesLoading(true);
    try {
      const data = await apiClient(`/issues/student/${studentId}`);
      if (data && data.issues) {
        setMyIssues(data.issues);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIssuesLoading(false);
    }
  };

  const fetchGrades = async () => {
    setGradesLoading(true);
    try {
      const data = await apiClient(`/academic/grades/${studentId}`);
      setGrades(data);
    } catch (error) {
      console.error(error);
      // It returns 404 if no grades found
      setGrades(null);
    } finally {
      setGradesLoading(false);
    }
  };

  const handleSendAI = async (text?: string) => {
    const msg = (text ?? input).trim();
    if (!msg || isTyping) return;

    setMessages((prev) => [...prev, { role: 'user', content: msg, timestamp: new Date().toISOString() }]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await apiClient('/chat/student', {
        method: 'POST',
        body: JSON.stringify({
          message: msg,
          student_id: studentId
        }),
      });

      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: response.content || response.answer,
        actions: response.quick_actions || response.actions,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Xin lỗi, hệ thống AI đang bảo trì. Vui lòng thử lại sau!',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendAI();
    }
  };

  const handleSubmitForm = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');

    if (formTitle.length < 3) {
      setFormError('Tiêu đề phải có ít nhất 3 ký tự');
      return;
    }
    if (formContent.length < 10) {
      setFormError('Nội dung phải có ít nhất 10 ký tự để GVCN hiểu rõ vấn đề');
      return;
    }

    setFormLoading(true);
    try {
      const res = await apiClient('/issues/form', {
        method: 'POST',
        body: JSON.stringify({
          student_id: studentId,
          title: formTitle,
          content: formContent
        })
      });
      if (res.success) {
        setFormSuccess('Vấn đề của bạn đã được gửi thành công đến GVCN!');
        setFormTitle('');
        setFormContent('');
        // Tự động tải lại danh sách
        fetchMyIssues();
      }
    } catch (err: any) {
      setFormError(err.message || 'Có lỗi xảy ra khi gửi thông tin!');
    } finally {
      setFormLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (newPassword !== confirmPassword) {
      setPasswordError('Mật khẩu nhập lại không khớp');
      return;
    }

    setPasswordLoading(true);
    try {
      const res = await apiClient('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({
          uid: studentUid,
          new_password: newPassword
        })
      });
      if (res.success) {
        setPasswordSuccess('Đổi mật khẩu thành công!');
        setNewPassword('');
        setConfirmPassword('');
        setTimeout(() => setShowPasswordModal(false), 2000);
      }
    } catch (err: any) {
      setPasswordError(err.message || 'Có lỗi xảy ra khi đổi mật khẩu');
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col max-w-4xl mx-auto px-4 bg-navy-950">
      {/* --- Header --- */}
      <motion.header
        className="flex items-center justify-between py-4 border-b border-white/[0.06] sticky top-0 z-20 bg-navy-950"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-blue-500
                          flex items-center justify-center shadow-glow-purple/30">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-white font-bold">{studentName}</p>
            <p className="text-xs text-slate-400">MSSV: {studentId}</p>
          </div>
        </div>

        <div className="flex gap-4 items-center">
          {/* Notification Bell */}
          <div className="relative" ref={notifRef}>
            <button 
              onClick={() => setShowNotif(!showNotif)}
              className={`relative p-2 text-slate-400 hover:text-white rounded-full hover:bg-white/5 transition-colors group
                          ${showNotif ? 'bg-white/10 text-white' : ''}`}
            >
              <Bell className={`w-5 h-5 ${notifications.filter(n => !n.read).length > 0 ? 'group-hover:animate-wiggle' : ''}`} />
              {notifications.filter(n => !n.read).length > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-navy-900"></span>
              )}
            </button>

            {/* Notification Dropdown */}
            <AnimatePresence>
              {showNotif && (
                <motion.div
                  className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] bg-navy-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden z-50"
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="flex items-center justify-between p-4 border-b border-white/5 bg-navy-800/50">
                    <h3 className="text-white font-semibold text-sm">Thông báo</h3>
                  </div>
                  <div className="max-h-80 overflow-y-auto custom-scrollbar">
                    {notifications.length === 0 ? (
                      <div className="p-6 text-center text-slate-400 text-sm">Chưa có thông báo nào.</div>
                    ) : (
                      notifications.map((notif) => (
                        <div 
                          key={notif.id} 
                          className={`p-4 border-b border-white/5 hover:bg-white/[0.02] transition-colors flex gap-3 group/item
                                     ${!notif.read ? 'bg-purple-500/5' : ''}`}
                        >
                          <div className="shrink-0 mt-1">
                            {notif.type === 'announcement' ? <Bell className="w-4 h-4 text-purple-400" /> : 
                             notif.type === 'urgent' ? <AlertTriangle className="w-4 h-4 text-red-400" /> :
                             <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm mb-1 ${!notif.read ? 'text-white font-semibold' : 'text-slate-300 font-medium'}`}>
                              {notif.title}
                            </p>
                            <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed whitespace-pre-wrap">{notif.desc}</p>
                            <p className="text-[10px] text-slate-500 mt-2">{notif.time}</p>
                          </div>
                          <div className="flex flex-col gap-2 items-center opacity-100 sm:opacity-0 sm:group-hover/item:opacity-100 transition-opacity">
                            {!notif.read && (
                              <button onClick={(e) => handleMarkAsRead(notif.id, e)} className="p-1.5 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 rounded-md tooltip" title="Đánh dấu đã đọc">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                              </button>
                            )}
                            <button onClick={(e) => handleDeleteNotification(notif.id, e)} className="p-1.5 bg-red-500/10 text-red-400 hover:bg-red-500/20 rounded-md tooltip" title="Xóa">
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="h-6 w-px bg-white/10 hidden sm:block"></div>

          <div className="relative" ref={profileRef}>
            <button 
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            >
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 p-[1px]">
                <div className="w-full h-full rounded-full bg-navy-900 flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              </div>
            </button>
            
            <AnimatePresence>
              {showProfileMenu && (
                <motion.div
                  className="absolute right-0 mt-2 w-48 bg-navy-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden py-1 z-50"
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="px-4 py-3 border-b border-white/5 mb-1">
                    <p className="text-sm font-medium text-white truncate">{studentName}</p>
                    <p className="text-xs text-slate-400">Sinh viên</p>
                  </div>
                  
                  <button 
                    onClick={() => { setShowProfileMenu(false); setShowPasswordModal(true); }}
                    className="w-full text-left px-4 py-2 text-sm flex items-center gap-2 text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
                  >
                    <Key className="w-4 h-4" /> Đổi mật khẩu
                  </button>
                  <button 
                    onClick={() => { setShowProfileMenu(false); sessionStorage.clear(); router.push('/login'); }}
                    className="w-full text-left px-4 py-2 text-sm flex items-center gap-2 text-red-400 hover:bg-red-400/10 transition-colors"
                  >
                    <LogOut className="w-4 h-4" /> Đăng xuất
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.header>

      {/* --- Tab Navigation --- */}
      <div className="flex bg-navy-900/50 p-1.5 rounded-2xl my-6 border border-white/[0.05]">
        <button
          onClick={() => setActiveTab('ai')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${activeTab === 'ai' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'
            }`}
        >
          <Bot className="w-4 h-4" /> Hỏi Pet hỗ trợ
        </button>
        <button
          onClick={() => setActiveTab('form')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${activeTab === 'form' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'
            }`}
        >
          <MessageSquare className="w-4 h-4" /> Liên hệ GVCN
        </button>
        <button
          onClick={() => setActiveTab('grades')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${activeTab === 'grades' ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'
            }`}
        >
          <BookOpen className="w-4 h-4" /> Bảng điểm
        </button>
        <button
          onClick={() => setActiveTab('my-issues')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium rounded-xl transition-all ${activeTab === 'my-issues' ? 'bg-orange-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'
            }`}
        >
          <AlertCircle className="w-4 h-4" /> Vấn đề của tôi
        </button>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col relative">
        <AnimatePresence mode="wait">

          {/* TAB 1: AI CHAT */}
          {activeTab === 'ai' && (
            <motion.div
              key="tab-ai"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="flex flex-col h-full absolute inset-0"
            >
              <div className="flex gap-2 py-2 overflow-x-auto scrollbar-none">
                {QUICK_ACTIONS.map(({ label, icon: Icon }) => (
                  <button
                    key={label}
                    onClick={() => handleSendAI(label)}
                    className="flex items-center gap-2 px-4 py-2 rounded-full shrink-0
                               bg-navy-800/60 border border-white/[0.08] text-slate-300 text-sm
                               hover:bg-navy-700/60 hover:border-purple-500/30 hover:text-white"
                  >
                    <Icon className="w-3.5 h-3.5 text-purple-400" /> {label}
                  </button>
                ))}
              </div>

              <div className="flex-1 space-y-5 py-4 overflow-y-auto pr-2 custom-scrollbar">
                {messages.length === 0 && (
                  <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-3">
                    <Bot className="w-12 h-12 text-slate-700" />
                    <p>Chào bạn, mình là Pet cưng của GVCN. Mình có thể giúp gì cho bạn?</p>
                  </div>
                )}
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1
                      ${msg.role === 'user' ? 'bg-purple-500/20 border border-purple-500/30' : 'bg-blue-500/20 border border-blue-500/30'}`}>
                      {msg.role === 'user' ? <User className="w-4 h-4 text-purple-300" /> : <Bot className="w-4 h-4 text-blue-300" />}
                    </div>
                    <div className={`max-w-[80%] space-y-2 flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                      <div className={`px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap
                        ${msg.role === 'user' ? 'bubble-user' : 'bubble-ai'}`}>
                        {msg.content}
                      </div>
                      {msg.actions && msg.actions.length > 0 && (
                        <div className="flex flex-wrap gap-1.5">
                          {msg.actions.map((action, i) => (
                            <button
                              key={i}
                              onClick={() => handleSendAI(action)}
                              className="text-xs px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 hover:bg-purple-500/20"
                            >
                              {action}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center shrink-0">
                      <Sparkles className="w-4 h-4 text-blue-300 animate-pulse" />
                    </div>
                    <div className="bubble-ai px-4 py-3">
                      <div className="flex gap-1.5 items-center h-4">
                        <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>

              <div className="py-4 border-t border-white/[0.06]">
                <div className="flex gap-3 items-end">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Nhắn tin với Pet... (Enter để gửi)"
                    rows={1}
                    disabled={isTyping}
                    className="input-dark flex-1 resize-none leading-relaxed max-h-32 overflow-y-auto"
                    style={{ fieldSizing: 'content' } as React.CSSProperties}
                  />
                  <button onClick={() => handleSendAI()} disabled={!input.trim() || isTyping} className="btn-primary p-3 shrink-0 disabled:opacity-40">
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* TAB 2: GỬI GVCN FORM */}
          {activeTab === 'form' && (
            <motion.div
              key="tab-form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="flex flex-col h-full absolute inset-0 overflow-y-auto pb-10"
            >
              <div className="glass-card p-6 md:p-8 max-w-2xl mx-auto w-full mt-4">
                <div className="flex items-center gap-3 mb-6 border-b border-white/10 pb-4">
                  <div className="p-3 bg-purple-500/20 rounded-xl">
                    <MessageSquare className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">Gửi vấn đề đến GVCN</h2>
                    <p className="text-sm text-slate-400">Tin nhắn này sẽ được gửi trực tiếp đến hộp thư của GVCN</p>
                  </div>
                </div>

                {formSuccess ? (
                  <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-6 text-center">
                    <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
                    <h3 className="text-emerald-400 font-semibold mb-2">{formSuccess}</h3>
                    <p className="text-slate-400 text-sm mb-6">Giáo viên sẽ nhận được thông báo và phản hồi lại cho bạn sớm nhất có thể.</p>
                    <button onClick={() => setFormSuccess('')} className="btn-primary bg-emerald-600 hover:bg-emerald-500 px-6">
                      Gửi tin nhắn khác
                    </button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmitForm} className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Tiêu đề</label>
                      <input
                        type="text"
                        value={formTitle}
                        onChange={(e) => setFormTitle(e.target.value)}
                        className="input-dark w-full"
                        placeholder="Ví dụ: Tư vấn về tâm lý học tập..."
                        disabled={formLoading}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Nội dung chi tiết</label>
                      <textarea
                        value={formContent}
                        onChange={(e) => setFormContent(e.target.value)}
                        className="input-dark w-full min-h-[150px] resize-y"
                        placeholder="Mô tả chi tiết vấn đề của bạn để GVCN có thể hỗ trợ tốt nhất..."
                        disabled={formLoading}
                        required
                      />
                    </div>
                    {formError && (
                      <p className="text-red-400 text-sm flex items-center gap-2"><AlertCircle className="w-4 h-4" /> {formError}</p>
                    )}
                    <button
                      type="submit"
                      disabled={formLoading}
                      className="w-full btn-primary bg-purple-600 hover:bg-purple-500 py-3 disabled:opacity-50"
                    >
                      {formLoading ? 'Đang gửi...' : 'Gửi thông tin cho GVCN'}
                    </button>
                  </form>
                )}
              </div>
            </motion.div>
          )}

          {/* TAB 3: GRADES */}
          {activeTab === 'grades' && (
            <motion.div
              key="tab-grades"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex flex-col h-full absolute inset-0 overflow-y-auto pb-10"
            >
              <div className="glass-card p-6 md:p-8 max-w-2xl mx-auto w-full mt-4">
                <div className="flex items-center justify-between mb-8 pb-4 border-b border-white/10">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-emerald-500/20 rounded-xl">
                      <BookOpen className="w-6 h-6 text-emerald-400" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white">Kết quả học tập</h2>
                      <p className="text-sm text-slate-400">Điểm số</p>
                    </div>
                  </div>
                  {grades && (
                    <div className="text-right">
                      <p className="text-sm text-slate-400">Điểm trung bình (GPA)</p>
                      <p className={`text-3xl font-bold ${grades.gpa >= 8 ? 'text-emerald-400' : grades.gpa >= 5 ? 'text-blue-400' : 'text-red-400'}`}>
                        {grades.gpa.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>

                {gradesLoading ? (
                  <div className="flex flex-col items-center justify-center py-12 text-slate-400">
                    <RefreshCw className="w-8 h-8 animate-spin mb-4 text-emerald-500/50" />
                    <p>Đang tải bảng điểm...</p>
                  </div>
                ) : !grades ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-navy-800 rounded-full flex items-center justify-center mx-auto mb-4">
                      <BookOpen className="w-8 h-8 text-slate-500" />
                    </div>
                    <p className="text-slate-300 font-medium text-lg">Chưa có dữ liệu điểm</p>
                    <p className="text-slate-500 text-sm mt-2">Hiện tại hệ thống chưa nhận được dữ liệu điểm của bạn.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-12 gap-4 px-4 py-2 bg-navy-900/50 rounded-lg text-sm font-medium text-slate-400">
                      <div className="col-span-8">Môn học</div>
                      <div className="col-span-4 text-right">Điểm số</div>
                    </div>
                    {grades.subjects.map((sub, idx) => (
                      <div key={idx} className="grid grid-cols-12 gap-4 px-4 py-3 border-b border-white/[0.05] hover:bg-white/[0.02] transition-colors items-center">
                        <div className="col-span-8 text-slate-200 font-medium">{sub.subject_name}</div>
                        <div className="col-span-4 text-right">
                          <span className={`inline-block px-3 py-1 rounded-full font-bold text-sm ${sub.score >= 8 ? 'bg-emerald-500/10 text-emerald-400' :
                            sub.score >= 5 ? 'bg-blue-500/10 text-blue-400' :
                              'bg-red-500/10 text-red-400'
                            }`}>
                            {sub.score.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    ))}
                    {grades.updated_at && (
                      <p className="text-xs text-slate-500 text-right mt-4 pt-4">
                        Cập nhật lần cuối: {new Date(grades.updated_at).toLocaleDateString('vi-VN')}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* TAB 4: MY ISSUES */}
          {activeTab === 'my-issues' && (
            <motion.div
              key="tab-my-issues"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="flex flex-col h-full absolute inset-0 overflow-y-auto pb-10"
            >
              <div className="glass-card p-6 md:p-8 max-w-4xl mx-auto w-full mt-4">
                <div className="flex items-center gap-3 mb-6 border-b border-white/10 pb-4">
                  <div className="p-3 bg-orange-500/20 rounded-xl">
                    <AlertCircle className="w-6 h-6 text-orange-400" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">Danh sách vấn đề đã gửi</h2>
                    <p className="text-sm text-slate-400">Theo dõi trạng thái và trao đổi với GVCN</p>
                  </div>
                </div>

                {issuesLoading ? (
                  <div className="flex flex-col items-center justify-center py-12 text-slate-400">
                    <RefreshCw className="w-8 h-8 animate-spin mb-4 text-orange-500/50" />
                    <p>Đang tải danh sách...</p>
                  </div>
                ) : (
                  <IssueTable 
                    issues={myIssues} 
                    onResolve={() => {}} // SV không được phép tự đóng issue
                    isResolvingId={undefined}
                    currentUserId={studentId}
                    currentUserRole="STUDENT"
                  />
                )}
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>

      {/* Password Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card w-full max-w-md p-6 relative"
          >
            <button
              onClick={() => setShowPasswordModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Key className="w-5 h-5 text-purple-400" /> Đổi mật khẩu
            </h2>

            {passwordSuccess ? (
              <div className="text-center py-6">
                <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
                <p className="text-emerald-400 font-medium">{passwordSuccess}</p>
              </div>
            ) : (
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Mật khẩu mới</label>
                  <div className="relative">
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="input-dark w-full pr-11"
                      placeholder="Tối thiểu 8 ký tự, 1 chữ hoa, 1 số..."
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      {showNewPassword ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Nhập lại mật khẩu</label>
                  <div className="relative">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="input-dark w-full pr-11"
                      placeholder="Xác nhận mật khẩu mới"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      {showConfirmPassword ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
                    </button>
                  </div>
                </div>
                {passwordError && (
                  <p className="text-red-400 text-sm flex items-center gap-2"><AlertCircle className="w-4 h-4" /> {passwordError}</p>
                )}
                <button
                  type="submit"
                  disabled={passwordLoading}
                  className="w-full btn-primary bg-purple-600 hover:bg-purple-500 py-2.5 mt-2 disabled:opacity-50"
                >
                  {passwordLoading ? 'Đang cập nhật...' : 'Cập nhật mật khẩu'}
                </button>
              </form>
            )}
          </motion.div>
        </div>
      )}
    </div>
  );
}