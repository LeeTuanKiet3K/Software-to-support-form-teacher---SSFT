'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, MessageSquare, GraduationCap,
  Bell, LogOut, ChevronRight, Users, BookOpen, Calendar,
  AlertTriangle, CheckCircle2
} from 'lucide-react';

import { apiClient } from '@/lib/apiClient';

const INITIAL_NOTIFICATIONS: any[] = [];

const advisorNav = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dashboard/chat', label: 'Trợ lý AI', icon: MessageSquare },
  { href: '/dashboard/students', label: 'Sinh viên', icon: Users },
  { href: '/dashboard/academic', label: 'Học vụ', icon: BookOpen },
  { href: '/dashboard/calendar', label: 'Lịch trình', icon: Calendar },
];

export function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();

  const [showNotif, setShowNotif] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);
  const [advisorName, setAdvisorName] = useState('GVCN');
  const [advisorInitials, setAdvisorInitials] = useState('U');
  
  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = async () => {
    try {
      const classId = sessionStorage.getItem('ssft_class_id') || '';
      const data = await apiClient(`/notifications/list?class_id=${classId}`);
      if (data && data.notifications) {
        setNotifications(data.notifications);
      }
    } catch (error) {
      console.error("Lỗi lấy thông báo:", error);
    }
  };

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

    document.addEventListener('mousedown', handleClickOutside);

    const storedName = sessionStorage.getItem('ssft_name');
    if (storedName) {
      setAdvisorName(storedName);
      const nameParts = storedName.trim().split(' ');
      if (nameParts.length > 0) {
        const lastPart = nameParts[nameParts.length - 1];
        setAdvisorInitials(lastPart.substring(0, 1).toUpperCase());
      }
    }

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      clearInterval(interval);
    };
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <motion.aside
      className="w-64 shrink-0 h-screen sticky top-0 flex flex-col
                 bg-navy-900/80 backdrop-blur-xl border-r border-white/[0.05]"
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* --- Logo --- */}
      <div className="px-6 py-5 border-b border-white/[0.05]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 to-blue-500
                          flex items-center justify-center shadow-glow-purple/30">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-sm tracking-wide">DASHBOARD</p>
          </div>
        </div>
      </div>

      {/* --- Navigation --- */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {advisorNav.map((item) => {
          const isActive = pathname === item.href;
          return (
            <button
              key={item.href}
              onClick={() => router.push(item.href)}
              className={`nav-item w-full ${isActive ? 'active' : ''}`}
            >
              <item.icon className="w-4.5 h-4.5 w-[18px] h-[18px] shrink-0" />
              <span className="flex-1 text-left text-sm">{item.label}</span>
              {isActive && <ChevronRight className="w-3.5 h-3.5 opacity-50" />}
            </button>
          );
        })}
      </nav>

      {/* --- Bottom Features (Notifications & Profile) --- */}
      <div className="p-4 border-t border-white/[0.05] flex items-center justify-between gap-2">
        {/* Profile Dropdown */}
        <div className="relative flex-1" ref={profileRef}>
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-3 w-full hover:bg-white/5 p-2 rounded-xl transition-colors"
          >
            <div className="w-9 h-9 shrink-0 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 p-[1px]">
              <div className="w-full h-full rounded-full bg-navy-900 flex items-center justify-center">
                <span className="text-sm font-bold text-white">{advisorInitials}</span>
              </div>
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-sm font-semibold text-white truncate">{advisorName}</p>
              <p className="text-[10px] text-slate-400 truncate">Giáo viên chủ nhiệm</p>
            </div>
          </button>

          <AnimatePresence>
            {showProfileMenu && (
              <motion.div
                className="absolute bottom-full left-0 mb-2 w-56 bg-navy-900 border border-white/10 rounded-2xl shadow-[0_-10px_40px_rgba(0,0,0,0.5)] overflow-hidden py-1 z-50"
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.2 }}
              >
                <div className="px-4 py-3 border-b border-white/5 mb-1">
                  <p className="text-sm font-medium text-white">{advisorName}</p>
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
                  className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-400/10 transition-colors flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  Đăng xuất
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Notifications Dropdown */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setShowNotif(!showNotif)}
            className={`relative p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors group
                        ${showNotif ? 'bg-white/10 text-white' : ''}`}
          >
            <Bell className={`w-5 h-5 ${unreadCount > 0 ? 'group-hover:animate-wiggle' : ''}`} />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-navy-900"></span>
            )}
          </button>

          <AnimatePresence>
            {showNotif && (
              <motion.div
                className="absolute bottom-full left-0 mb-2 w-80 sm:w-96 bg-navy-900 border border-white/10 rounded-2xl shadow-[0_-10px_40px_rgba(0,0,0,0.5)] overflow-hidden z-50"
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
                  {notifications.length === 0 && (
                     <div className="p-6 text-center text-slate-400 text-sm">Không có thông báo nào</div>
                  )}
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
      </div>
    </motion.aside>
  );
}
