'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Bell, Menu, AlertTriangle, MessageSquare, CheckCircle2 } from 'lucide-react';

const MOCK_NOTIFICATIONS = [
  { id: 1, title: 'Cảnh báo khẩn cấp (P0)', desc: 'Sinh viên Trần Quang Tuấn báo cáo căng thẳng kéo dài.', time: '5 phút trước', type: 'urgent', read: false },
  { id: 2, title: 'Cập nhật hệ thống', desc: 'Đã hoàn tất tính toán GPA học kỳ 1.', time: '2 giờ trước', type: 'system', read: true },
  { id: 3, title: 'Tin nhắn mới', desc: 'Có 3 sinh viên vừa nhắn tin cho Trợ lý AI.', time: '3 giờ trước', type: 'message', read: true },
];

export function Header() {
  const [showNotif, setShowNotif] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotif(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = MOCK_NOTIFICATIONS.filter(n => !n.read).length;

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
            type="text" 
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
                  <button className="text-xs text-purple-400 hover:text-purple-300 font-medium">Đánh dấu đã đọc</button>
                </div>
                <div className="max-h-80 overflow-y-auto custom-scrollbar">
                  {MOCK_NOTIFICATIONS.map((notif) => (
                    <div 
                      key={notif.id} 
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
                  <button className="text-xs text-slate-400 hover:text-white font-medium transition-colors">Xem tất cả</button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        <div className="h-6 w-px bg-white/10"></div>
        
        <button className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 p-[1px]">
            <div className="w-full h-full rounded-full bg-navy-900 flex items-center justify-center">
              <span className="text-xs font-bold text-white">LN</span>
            </div>
          </div>
        </button>
      </div>
    </motion.header>
  );
}
