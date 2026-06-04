'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Bell, Menu, AlertTriangle, MessageSquare, CheckCircle2 } from 'lucide-react';

import { useRouter } from 'next/navigation';

const INITIAL_NOTIFICATIONS = [
  { id: 1, title: 'Cảnh báo khẩn cấp (P0)', desc: 'Sinh viên Trần Quang Tuấn báo cáo căng thẳng kéo dài.', time: '5 phút trước', type: 'urgent', read: false, url: '/dashboard/students?search=Trần Quang Tuấn' },
  { id: 2, title: 'Cập nhật hệ thống', desc: 'Đã hoàn tất tính toán GPA học kỳ 1.', time: '2 giờ trước', type: 'system', read: true, url: '/dashboard/academic' },
  { id: 3, title: 'Tin nhắn mới', desc: 'Có 3 sinh viên vừa nhắn tin cho Trợ lý AI.', time: '3 giờ trước', type: 'message', read: true, url: '/dashboard/chat?prompt=Tóm tắt tin nhắn AI' },
];

export function Header() {
  const router = useRouter();
  const [showNotif, setShowNotif] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [globalSearch, setGlobalSearch] = useState('');
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);
  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const handleMarkAllAsRead = (e: React.MouseEvent) => {
    e.stopPropagation();
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const handleNotificationClick = (notif: typeof INITIAL_NOTIFICATIONS[0]) => {
    setNotifications(prev => prev.map(n => n.id === notif.id ? { ...n, read: true } : n));
    setShowNotif(false);
    if (notif.url) {
      router.push(notif.url);
    }
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotif(false);
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfileMenu(false);
      }
    };
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <motion.header 
      className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 
                 bg-navy-900/60 backdrop-blur-md border-b border-white/[0.05]"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-center gap-4 flex-1">
        <button className="lg:hidden p-2 -ml-2 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors">
          <Menu className="w-5 h-5" />
        </button>
        <div className="relative w-full max-w-md hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input 
            ref={searchRef}
            type="text" 
            value={globalSearch}
            onChange={(e) => setGlobalSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && globalSearch.trim()) {
                router.push(`/dashboard/students?search=${globalSearch.trim()}`);
                setGlobalSearch('');
                searchRef.current?.blur();
              }
            }}
            placeholder="Tìm kiếm sinh viên, mã số, vấn đề... (Ctrl+K)" 
            className="w-full bg-navy-800/50 border border-white/10 text-sm text-white placeholder-slate-500 
                       rounded-full pl-10 pr-4 py-2 focus:outline-none focus:ring-1 focus:ring-purple-500/50 transition-all"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1">
            <span className="px-1.5 py-0.5 rounded-md bg-white/10 text-[10px] text-slate-400 font-medium">Ctrl</span>
            <span className="px-1.5 py-0.5 rounded-md bg-white/10 text-[10px] text-slate-400 font-medium">K</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Notification Bell */}
        <div className="relative" ref={notifRef}>
          <button 
            onClick={() => setShowNotif(!showNotif)}
            className={`relative p-2 text-slate-400 hover:text-white rounded-full hover:bg-white/5 transition-colors group
                        ${showNotif ? 'bg-white/10 text-white' : ''}`}
          >
            <Bell className={`w-5 h-5 ${unreadCount > 0 ? 'group-hover:animate-wiggle' : ''}`} />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-navy-900"></span>
            )}
          </button>

          {/* Notification Dropdown */}
          <AnimatePresence>
            {showNotif && (
              <motion.div
                className="absolute right-0 mt-2 w-80 bg-navy-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
              >
                <div className="flex items-center justify-between p-4 border-b border-white/5 bg-navy-800/50">
                  <h3 className="text-white font-semibold text-sm">Thông báo</h3>
                  <button 
                    onClick={handleMarkAllAsRead}
                    className="text-xs text-purple-400 hover:text-purple-300 font-medium transition-colors"
                  >
                    Đánh dấu đã đọc
                  </button>
                </div>
                <div className="max-h-80 overflow-y-auto custom-scrollbar">
                  {notifications.map((notif) => (
                    <div 
                      key={notif.id} 
                      onClick={() => handleNotificationClick(notif)}
                      className={`p-4 border-b border-white/5 hover:bg-white/[0.02] cursor-pointer transition-colors flex gap-3
                                 ${!notif.read ? 'bg-purple-500/5' : ''}`}
                    >
                      <div className="shrink-0 mt-1">
                        {notif.type === 'urgent' && <AlertTriangle className="w-4 h-4 text-red-400" />}
                        {notif.type === 'system' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                        {notif.type === 'message' && <MessageSquare className="w-4 h-4 text-blue-400" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm mb-1 ${!notif.read ? 'text-white font-semibold' : 'text-slate-300 font-medium'}`}>
                          {notif.title}
                        </p>
                        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{notif.desc}</p>
                        <p className="text-[10px] text-slate-500 mt-2">{notif.time}</p>
                      </div>
                      {!notif.read && (
                        <div className="w-2 h-2 rounded-full bg-purple-500 mt-1.5 shrink-0 shadow-[0_0_8px_rgba(168,85,247,0.6)]"></div>
                      )}
                    </div>
                  ))}
                </div>
                <div className="p-3 bg-navy-900 border-t border-white/5 text-center">
                  <button 
                    onClick={() => { setShowNotif(false); router.push('/dashboard/notifications'); }}
                    className="text-xs text-slate-400 hover:text-white font-medium transition-colors"
                  >
                    Xem tất cả
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        <div className="h-6 w-px bg-white/10"></div>
        
        <div className="relative" ref={profileRef}>
          <button 
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 p-[1px]">
              <div className="w-full h-full rounded-full bg-navy-900 flex items-center justify-center">
                <span className="text-xs font-bold text-white">LN</span>
              </div>
            </div>
          </button>
          
          <AnimatePresence>
            {showProfileMenu && (
              <motion.div
                className="absolute right-0 mt-2 w-48 bg-navy-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden py-1"
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
              >
                <div className="px-4 py-3 border-b border-white/5 mb-1">
                  <p className="text-sm font-medium text-white">ThS. Lan Nguyễn</p>
                  <p className="text-xs text-slate-400">Giáo viên chủ nhiệm</p>
                </div>
                
                <button 
                  onClick={() => { setShowProfileMenu(false); router.push('/dashboard?action=change-password'); }}
                  className="w-full text-left px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
                >
                  Đổi mật khẩu
                </button>
                <button 
                  onClick={() => { setShowProfileMenu(false); sessionStorage.clear(); router.push('/login'); }}
                  className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-400/10 transition-colors"
                >
                  Đăng xuất
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.header>
  );
}
