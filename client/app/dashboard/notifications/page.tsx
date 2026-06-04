'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, AlertTriangle, CheckCircle2, MessageSquare, Check, Trash2, Filter } from 'lucide-react';

const INITIAL_NOTIFICATIONS = [
  { id: 1, title: 'Cảnh báo khẩn cấp (P0)', desc: 'Sinh viên Trần Quang Tuấn báo cáo căng thẳng kéo dài. Vui lòng liên hệ với sinh viên sớm nhất có thể.', time: '5 phút trước', type: 'urgent', read: false },
  { id: 2, title: 'Cập nhật hệ thống', desc: 'Đã hoàn tất tính toán GPA học kỳ 1 cho toàn bộ sinh viên lớp 24CTT4.', time: '2 giờ trước', type: 'system', read: true },
  { id: 3, title: 'Tin nhắn mới', desc: 'Có 3 sinh viên vừa nhắn tin cho Trợ lý AI hỏi về thủ tục bảo lưu học kỳ.', time: '3 giờ trước', type: 'message', read: true },
  { id: 4, title: 'Phiếu khiếu nại mới', desc: 'Sinh viên Lê Thị Bích gửi yêu cầu chấm phúc khảo môn Toán rời rạc.', time: '1 ngày trước', type: 'urgent', read: true },
  { id: 5, title: 'Nhắc nhở nộp báo cáo', desc: 'Hạn chót nộp báo cáo tình hình lớp tháng 5 là vào thứ 6 tuần này.', time: '2 ngày trước', type: 'system', read: true },
];

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const handleMarkAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const handleMarkAsRead = (id: number) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const handleDelete = (id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const filteredNotifs = notifications.filter(n => filter === 'all' ? true : !n.read);

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2 mb-1">
            <Bell className="w-6 h-6 text-purple-400" />
            Trung tâm thông báo
          </h1>
          <p className="text-slate-400 text-sm">Quản lý tất cả thông báo và cảnh báo từ hệ thống</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="bg-navy-900 border border-white/10 rounded-lg p-1 flex">
            <button 
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${filter === 'all' ? 'bg-white/10 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Tất cả
            </button>
            <button 
              onClick={() => setFilter('unread')}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${filter === 'unread' ? 'bg-white/10 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Chưa đọc
            </button>
          </div>
          
          <button 
            onClick={handleMarkAllAsRead}
            className="btn-ghost flex items-center gap-2 text-sm bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 px-4 py-2 rounded-lg transition-colors border border-purple-500/20"
          >
            <Check className="w-4 h-4" />
            Đánh dấu tất cả đã đọc
          </button>
        </div>
      </div>

      {/* Notifications List */}
      <div className="glass-card flex-1 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
          {filteredNotifs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <CheckCircle2 className="w-12 h-12 mb-3 text-emerald-500/50" />
              <p>Tuyệt vời! Bạn không có thông báo nào cần đọc.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredNotifs.map((notif, idx) => (
                <motion.div
                  key={notif.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`p-4 md:p-5 rounded-xl border flex flex-col md:flex-row gap-4 md:items-start transition-colors group
                             ${!notif.read ? 'bg-purple-500/5 border-purple-500/30' : 'bg-navy-900/40 border-white/5 hover:border-white/10'}`}
                >
                  <div className={`shrink-0 w-10 h-10 rounded-full flex items-center justify-center
                                ${notif.type === 'urgent' ? 'bg-red-500/10 text-red-400' : 
                                  notif.type === 'system' ? 'bg-emerald-500/10 text-emerald-400' : 
                                  'bg-blue-500/10 text-blue-400'}`}
                  >
                    {notif.type === 'urgent' && <AlertTriangle className="w-5 h-5" />}
                    {notif.type === 'system' && <CheckCircle2 className="w-5 h-5" />}
                    {notif.type === 'message' && <MessageSquare className="w-5 h-5" />}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-1 gap-2">
                      <h3 className={`font-semibold text-sm md:text-base ${!notif.read ? 'text-white' : 'text-slate-200'}`}>
                        {notif.title}
                      </h3>
                      <span className="text-xs font-medium text-slate-500 whitespace-nowrap">{notif.time}</span>
                    </div>
                    <p className={`text-sm ${!notif.read ? 'text-slate-300' : 'text-slate-400'}`}>
                      {notif.desc}
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-2 md:opacity-0 md:group-hover:opacity-100 transition-opacity self-end md:self-center">
                    {!notif.read && (
                      <button 
                        onClick={() => handleMarkAsRead(notif.id)}
                        className="p-2 text-emerald-400 hover:bg-emerald-400/10 rounded-lg tooltip"
                        title="Đánh dấu đã đọc"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                    )}
                    <button 
                      onClick={() => handleDelete(notif.id)}
                      className="p-2 text-red-400 hover:bg-red-400/10 rounded-lg tooltip"
                      title="Xóa thông báo"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  
                  {/* Indicator for unread on mobile */}
                  {!notif.read && (
                    <div className="absolute top-4 right-4 w-2 h-2 rounded-full bg-purple-500 md:hidden"></div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
