'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, Clock, MapPin, Users, X, Trash2 } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

interface CalendarEvent {
  id: string;
  date: number; // storing date of month for simplicity
  title: string;
  time: string;
  location: string;
  type: string;
}

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Form State
  const [formDate, setFormDate] = useState('');
  const [formTime, setFormTime] = useState('');
  const [formTitle, setFormTitle] = useState('');
  const [formLocation, setFormLocation] = useState('');
  const [formType, setFormType] = useState('event');

  const fetchEvents = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient('/calendar/events');
      if (data && data.events) {
        setEvents(data.events);
      }
    } catch (error) {
      console.error('Lỗi khi tải danh sách sự kiện:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  // Basic calendar logic for current month
  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  
  const monthNames = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6", "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"];
  const weekDays = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  // Generate days array
  const days = [];
  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push(null);
  }
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formTitle || !formDate || !formTime || !formLocation) return;
    
    // Parse formDate to get just the day of month for the simple logic
    const selectedDay = parseInt(formDate.split('-')[2], 10);
    
    setIsSubmitting(true);
    try {
      await apiClient('/calendar/events', {
        method: 'POST',
        body: JSON.stringify({
          title: formTitle,
          date: selectedDay,
          time: formTime,
          location: formLocation,
          type: formType
        })
      });
      // Tải lại danh sách
      await fetchEvents();
      setIsModalOpen(false);
      
      // Reset form
      setFormTitle('');
      setFormDate('');
      setFormTime('');
      setFormLocation('');
      setFormType('event');
    } catch (error) {
      console.error('Lỗi khi tạo sự kiện:', error);
      alert('Không thể tạo sự kiện. Hãy thử lại.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!confirm('Bạn có chắc chắn muốn xóa sự kiện này?')) return;
    
    try {
      await apiClient(`/calendar/events/${eventId}`, {
        method: 'DELETE'
      });
      await fetchEvents();
    } catch (error) {
      console.error('Lỗi khi xóa sự kiện:', error);
      alert('Không thể xóa sự kiện. Hãy thử lại.');
    }
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Lịch trình & Sự kiện</h1>
          <p className="text-slate-400 text-sm">Quản lý lịch hẹn sinh viên và các mốc thời gian quan trọng</p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => setIsModalOpen(true)}
            className="btn-primary flex items-center gap-2 text-sm bg-purple-600 hover:bg-purple-700"
          >
            <Plus className="w-4 h-4" />
            Tạo sự kiện
          </button>
        </div>
      </div>

      <div className="flex flex-col xl:flex-row gap-6 flex-1 min-h-0">
        {/* Main Calendar Area */}
        <motion.div 
          className="glass-card flex-1 flex flex-col overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Calendar Header */}
          <div className="p-5 border-b border-white/5 flex items-center justify-between bg-navy-800/30">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-bold text-white">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={prevMonth} className="p-2 border border-white/10 rounded-lg text-slate-400 hover:bg-white/5 hover:text-white transition-colors">
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button className="px-4 py-2 border border-white/10 rounded-lg text-sm font-medium text-slate-300 hover:bg-white/5 hover:text-white transition-colors"
                      onClick={() => setCurrentDate(new Date())}>
                Hôm nay
              </button>
              <button onClick={nextMonth} className="p-2 border border-white/10 rounded-lg text-slate-400 hover:bg-white/5 hover:text-white transition-colors">
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Calendar Grid */}
          <div className="flex-1 overflow-y-auto p-5 relative">
            {isLoading && (
              <div className="absolute inset-0 bg-navy-900/50 backdrop-blur-sm flex items-center justify-center z-10">
                <p className="text-slate-300 font-medium">Đang tải...</p>
              </div>
            )}
            
            <div className="grid grid-cols-7 mb-4">
              {weekDays.map(day => (
                <div key={day} className="text-center text-sm font-semibold text-slate-400 py-2">
                  {day}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-2 lg:gap-3">
              {days.map((day, idx) => {
                const isToday = day === new Date().getDate() && 
                                currentDate.getMonth() === new Date().getMonth() && 
                                currentDate.getFullYear() === new Date().getFullYear();
                                
                const hasEvent = events.filter(e => e.date === day);
                
                return (
                  <div 
                    key={idx} 
                    className={`min-h-[80px] lg:min-h-[100px] p-2 rounded-xl border transition-colors relative group
                      ${day ? 'bg-navy-900/40 border-white/5 hover:border-purple-500/30 hover:bg-navy-800' : 'bg-transparent border-transparent'}
                      ${isToday ? 'border-purple-500/50 bg-purple-500/10' : ''}
                    `}
                  >
                    {day && (
                      <>
                        <div className={`text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full mb-1
                                       ${isToday ? 'bg-purple-500 text-white' : 'text-slate-300'}`}>
                          {day}
                        </div>
                        <div className="space-y-1 overflow-y-auto max-h-[60px] custom-scrollbar">
                          {hasEvent.map((ev, i) => (
                            <div key={i} className={`text-xs px-2 py-1 rounded truncate border flex justify-between items-center group/item
                              ${ev.type === 'meeting' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 
                                ev.type === 'deadline' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                                'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'}`}
                              title={`${ev.time} - ${ev.title}`}
                            >
                              <span className="truncate">{ev.title}</span>
                              <button 
                                onClick={(e) => { e.stopPropagation(); handleDeleteEvent(ev.id); }}
                                className="opacity-0 group-hover/item:opacity-100 p-0.5 hover:bg-white/20 rounded transition-opacity"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Sidebar Events */}
        <motion.div 
          className="w-full xl:w-80 flex flex-col gap-6 shrink-0"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="glass-card p-5 flex-1 overflow-hidden flex flex-col">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <CalendarIcon className="w-5 h-5 text-purple-400" />
              Sự kiện sắp tới
            </h3>
            
            <div className="space-y-4 overflow-y-auto pr-2 custom-scrollbar">
              {events.length === 0 && !isLoading && (
                 <p className="text-slate-400 text-sm text-center py-4">Chưa có sự kiện nào.</p>
              )}
              {events.map(ev => (
                <div key={ev.id} className="p-4 rounded-xl bg-navy-900/50 border border-white/5 hover:border-white/10 transition-colors relative group">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-sm font-semibold text-white leading-tight">{ev.title}</h4>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider font-bold shrink-0
                      ${ev.type === 'meeting' ? 'bg-blue-500/20 text-blue-400' : 
                        ev.type === 'deadline' ? 'bg-red-500/20 text-red-400' : 
                        'bg-emerald-500/20 text-emerald-400'}`}>
                      {ev.type}
                    </span>
                  </div>
                  
                  <div className="space-y-1.5 mt-3">
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{ev.date} Tháng {currentDate.getMonth() + 1}, {ev.time}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <MapPin className="w-3.5 h-3.5" />
                      <span>{ev.location}</span>
                    </div>
                  </div>
                  
                  <button 
                    onClick={() => handleDeleteEvent(ev.id)}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 p-1.5 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
          
          {/* Quick Stats/Summary */}
          <div className="glass-card p-5">
             <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
               <Users className="w-4 h-4 text-emerald-400" />
               Lịch hẹn chờ duyệt
             </h3>
             <div className="flex items-center justify-between p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
               <div>
                 <p className="text-xs text-orange-200">Sinh viên đăng ký tư vấn</p>
                 <p className="text-lg font-bold text-orange-400">3 yêu cầu</p>
               </div>
               <button className="text-xs font-medium bg-orange-500 hover:bg-orange-600 text-white px-3 py-1.5 rounded-md transition-colors">
                 Xem ngay
               </button>
             </div>
          </div>
        </motion.div>
      </div>

      {/* Create Event Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="bg-navy-900 border border-white/10 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden"
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
            >
              <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-navy-800/50">
                <h2 className="text-lg font-bold text-white">Tạo sự kiện mới</h2>
                <button 
                  onClick={() => setIsModalOpen(false)}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <form onSubmit={handleCreateEvent} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Tiêu đề sự kiện</label>
                  <input
                    type="text"
                    required
                    value={formTitle}
                    onChange={e => setFormTitle(e.target.value)}
                    className="input-dark bg-navy-950"
                    placeholder="VD: Họp phụ huynh..."
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">Ngày</label>
                    <input
                      type="date"
                      required
                      value={formDate}
                      onChange={e => setFormDate(e.target.value)}
                      className="input-dark bg-navy-950 [color-scheme:dark]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">Giờ</label>
                    <input
                      type="time"
                      required
                      value={formTime}
                      onChange={e => setFormTime(e.target.value)}
                      className="input-dark bg-navy-950 [color-scheme:dark]"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Địa điểm</label>
                  <input
                    type="text"
                    required
                    value={formLocation}
                    onChange={e => setFormLocation(e.target.value)}
                    className="input-dark bg-navy-950"
                    placeholder="VD: Phòng F.102"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Loại sự kiện</label>
                  <select
                    value={formType}
                    onChange={e => setFormType(e.target.value)}
                    className="input-dark bg-navy-950 w-full appearance-none"
                  >
                    <option value="event">Sự kiện thường</option>
                    <option value="meeting">Lịch hẹn tư vấn</option>
                    <option value="deadline">Hạn chót (Deadline)</option>
                  </select>
                </div>
                
                <div className="pt-4 flex gap-3">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="flex-1 px-4 py-2.5 rounded-xl border border-white/10 text-slate-300 font-medium hover:bg-white/5 transition-colors"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-medium transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? 'Đang lưu...' : 'Lưu sự kiện'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
