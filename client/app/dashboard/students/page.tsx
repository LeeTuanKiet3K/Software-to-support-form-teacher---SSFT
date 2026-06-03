'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, AreaChart, Area , Tooltip } from 'recharts';
import { User, BookOpen, HeartPulse, MessageSquare, Award, StickyNote, MapPin, Phone, Mail, GraduationCap, X, Search, Filter, ChevronRight, Maximize, Minimize } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

const radarData = [
  { subject: 'Học lực', value: 85 },
  { subject: 'Chuyên cần', value: 95 },
  { subject: 'Kỷ luật', value: 90 },
  { subject: 'Tâm lý', value: 50 },
  { subject: 'Giao tiếp', value: 70 },
  { subject: 'Hoạt động', value: 80 },
];

const gpaData = [
  { term: 'HK1', gpa: 3.2 }, { term: 'HK2', gpa: 3.5 },
  { term: 'HK3', gpa: 3.1 }, { term: 'HK4', gpa: 3.8 },
];

const chatHistory = [
  { id: 1, text: "Thưa cô, em muốn hỏi thủ tục bảo lưu học kỳ này ạ.", date: "Hôm nay", ai: "Đã hướng dẫn quy trình bảo lưu." },
  { id: 2, text: "Em cảm thấy áp lực quá, không theo kịp môn Cấu trúc dữ liệu...", date: "2 ngày trước", ai: "Phân loại: Nguy cơ tâm lý (Cao)." },
];

export default function StudentsPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<any | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setIsLoading(true);
        const data = await apiClient('/academic/class/24CTT4/students');
        const studentData = data || [];
        setStudents(studentData);
        
        // Auto-select student if search param is present
        if (typeof window !== 'undefined') {
          const params = new URLSearchParams(window.location.search);
          const searchQuery = params.get('search');
          if (searchQuery) {
            setSearchTerm(searchQuery);
            const match = studentData.find((s: any) => s.name?.includes(searchQuery) || s.id?.includes(searchQuery));
            if (match) setSelectedStudent(match);
          }
        }
      } catch (error) {
        console.error("Lỗi tải danh sách:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStudents();
  }, []);

  const filteredStudents = students.filter(s => 
    s.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    s.id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto h-[calc(100vh-73px)] flex flex-col">
      {/* Header Danh sách */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Danh sách Sinh viên</h1>
          <p className="text-slate-400 text-sm">Quản lý tổng quan lớp 24CTT4</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm MSSV, tên..."
              className="bg-navy-900 border border-white/10 text-sm text-white placeholder-slate-500 rounded-lg pl-9 pr-4 py-2 focus:outline-none focus:border-purple-500/50 w-64"
            />
          </div>
          <button className="p-2 bg-navy-900 border border-white/10 rounded-lg text-slate-400 hover:text-white transition-colors">
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Grid Danh sách Sinh viên */}
      {isLoading ? (
        <div className="flex-1 flex items-center justify-center text-slate-400">Đang tải danh sách sinh viên...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 overflow-y-auto custom-scrollbar pr-2 pb-6">
          {filteredStudents.length === 0 ? (
            <div className="col-span-full text-center py-10 text-slate-400">Không tìm thấy sinh viên nào phù hợp.</div>
          ) : (
            filteredStudents.map((student, idx) => (
            <motion.div
              key={student.id}
              className="glass-card p-5 cursor-pointer hover:border-purple-500/30 transition-all group"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => setSelectedStudent(student)}
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500 flex items-center justify-center text-white font-bold text-lg shadow-lg shrink-0">
                  {student.name ? student.name.charAt(0) : 'U'}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold truncate group-hover:text-purple-400 transition-colors">{student.name}</h3>
                  <p className="text-slate-400 text-sm mb-3">{student.id}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border
                      ${student.status === 'Nguy cơ' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                        student.status === 'Cảnh báo' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                        'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'}`}>
                      {student.status}
                    </span>
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-navy-800 border border-white/5 text-slate-300">
                      GPA: {student.gpa}
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-purple-400 transition-colors shrink-0" />
              </div>
            </motion.div>
          )))}
        </div>
      )}

      {/* Modal Profile Bento Box */}
      <AnimatePresence>
        {selectedStudent && (
          <div className="fixed inset-0 z-50 flex justify-end">
            <motion.div
              className="absolute inset-0 bg-navy-950/60 backdrop-blur-sm"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setSelectedStudent(null)}
            />
           
            <motion.div
              className={`relative bg-navy-950 h-full border-l border-white/10 shadow-2xl flex flex-col transition-all duration-500 ease-in-out ${isFullscreen ? 'w-full max-w-full' : 'w-full max-w-5xl'}`}
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            >
              {/* Header Profile Modal */}
              <div className="flex items-center justify-between p-6 border-b border-white/5 bg-navy-900/50 shrink-0">
                <div>
                  <h2 className="text-xl font-bold text-white">Hồ sơ Sinh viên Toàn diện</h2>
                  <p className="text-slate-400 text-sm">Góc nhìn 360 độ kết hợp phân tích AI</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsFullscreen(!isFullscreen)}
                    className="p-2 text-slate-400 hover:text-white bg-navy-800 rounded-lg hover:bg-navy-700 transition-colors"
                  >
                    {isFullscreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
                  </button>
                  <button
                    onClick={() => { setSelectedStudent(null); setIsFullscreen(false); }}
                    className="p-2 text-slate-400 hover:text-white bg-navy-800 rounded-lg hover:bg-red-500/80 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Bento Box Content */}
              <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 auto-rows-[160px]">
                 
                  {/* Ô 1: THÔNG TIN CÁ NHÂN */}
                  <motion.div
                    className="md:col-span-2 md:row-span-2 glass-card p-6 relative overflow-hidden group"
                    initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}
                  >
                    <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl transition-all duration-700" />
                   
                    <div className="flex gap-6 relative z-10 h-full">
                      <div className="shrink-0 flex flex-col items-center gap-3">
                        <div className="w-24 h-24 rounded-2xl bg-purple-500 p-1 shadow-glow-purple">
                          <div className="w-full h-full bg-navy-900 rounded-xl flex items-center justify-center overflow-hidden">
                            <User className="w-12 h-12 text-white/50" />
                          </div>
                        </div>
                        <div className="bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full flex items-center gap-1.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          <span className="text-xs font-medium text-emerald-400">Đang học</span>
                        </div>
                      </div>
                     
                      <div className="flex-1 flex flex-col justify-center">
                        <h2 className="text-2xl font-bold text-white mb-1">{selectedStudent.name}</h2>
                        <p className="text-purple-400 font-medium text-sm mb-4">MSSV: {selectedStudent.id} · Lớp 24CTT4</p>
                       
                        <div className="grid grid-cols-2 gap-y-3 text-sm text-slate-300">
                          <div className="flex items-center gap-2"><MapPin className="w-4 h-4 text-slate-500" /> KTX Khu B, Dĩ An</div>
                          <div className="flex items-center gap-2"><GraduationCap className="w-4 h-4 text-slate-500" /> CNTT - Khóa 2024</div>
                          <div className="flex items-center gap-2"><Phone className="w-4 h-4 text-slate-500" /> 0987 654 321</div>
                          <div className="flex items-center gap-2"><Mail className="w-4 h-4 text-slate-500" /> sv@hcmus.edu.vn</div>
                        </div>
                      </div>
                    </div>
                  </motion.div>

                  {/* Ô 2: ĐIỂM GPA */}
                  <motion.div
                    className="glass-card p-5 relative overflow-hidden group flex flex-col justify-between"
                    initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.15 }}
                  >
                    <div className="flex items-start justify-between relative z-10">
                      <div>
                        <p className="text-slate-400 text-sm font-medium mb-1">Điểm TB Tích lũy</p>
                        <h3 className="text-3xl font-bold text-white">{selectedStudent.gpa}</h3>
                      </div>
                      <div className="p-2.5 bg-purple-500/10 rounded-xl"><Award className="w-5 h-5 text-purple-400" /></div>
                    </div>
                    <p className={`text-xs font-medium relative z-10 ${selectedStudent.gpa < 2 ? 'text-red-400' : 'text-emerald-400'}`}>
                      {selectedStudent.gpa < 2 ? '↓ Giảm so với kỳ trước' : '↑ Tăng so với kỳ trước'}
                    </p>
                    <div className="absolute bottom-0 left-0 right-0 h-20 opacity-30 group-hover:opacity-60 transition-opacity">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={gpaData}>
                          <defs>
                            <linearGradient id="colorGpa" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8}/><stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <Area type="monotone" dataKey="gpa" stroke="#a855f7" fillOpacity={1} fill="url(#colorGpa)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </motion.div>

                  {/* Ô 3: CHỈ SỐ SỨC KHỎE TÂM LÝ */}
                  <motion.div
                    className={`glass-card p-5 transition-colors group
                      ${selectedStudent.stress === 'Cao' ? 'border-red-500/30 bg-red-500/5' :
                        selectedStudent.stress === 'Vừa' ? 'border-amber-500/30' : 'border-emerald-500/20'}`}
                    initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <p className="text-slate-400 text-sm font-medium">Stress & Tâm lý</p>
                      <div className={`p-2.5 rounded-xl ${selectedStudent.stress === 'Cao' ? 'bg-red-500/10 animate-pulse' : 'bg-emerald-500/10'}`}>
                        <HeartPulse className={`w-5 h-5 ${selectedStudent.stress === 'Cao' ? 'text-red-400' : 'text-emerald-400'}`} />
                      </div>
                    </div>
                    <h3 className={`text-2xl font-bold mb-1 ${selectedStudent.stress === 'Cao' ? 'text-red-400' : selectedStudent.stress === 'Vừa' ? 'text-amber-400' : 'text-emerald-400'}`}>
                      Mức độ {selectedStudent.stress}
                    </h3>
                    <p className="text-xs text-slate-400">Được phân tích từ tần suất chat gần nhất.</p>
                  </motion.div>

                  {/* Ô 4: LỊCH SỬ CHAT AI */}
                  <motion.div
                    className="md:col-span-2 md:row-span-2 glass-card p-6 flex flex-col"
                    initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.25 }}
                  >
                    <div className="flex items-center gap-2 mb-5">
                      <MessageSquare className="w-5 h-5 text-purple-400" />
                      <h3 className="text-slate-200 font-semibold">Lịch sử Tư vấn</h3>
                    </div>
                    <div className="flex-1 overflow-y-auto custom-scrollbar space-y-4 pr-2">
                      {chatHistory.map((chat) => (
                        <div key={chat.id} className="bg-navy-900/50 border border-white/5 rounded-xl p-4">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-xs font-semibold text-slate-400">Sinh viên hỏi:</span>
                            <span className="text-[10px] text-slate-500">{chat.date}</span>
                          </div>
                          <p className="text-sm text-slate-300 mb-3 italic">"{chat.text}"</p>
                          <div className="bg-purple-500/10 border-l-2 border-purple-500 pl-3 py-2 rounded-r-lg">
                            <span className="text-xs font-semibold text-purple-400 block mb-0.5">AI Phân tích:</span>
                            <span className="text-xs text-slate-400 block">{chat.ai}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Ô 5: RADAR CHART */}
                  <motion.div
                    className="md:col-span-1 md:row-span-2 glass-card p-6 flex flex-col"
                    initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }}
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <BookOpen className="w-5 h-5 text-blue-400" />
                      <h3 className="text-slate-200 font-semibold text-sm truncate">Phân tích Năng lực</h3>
                    </div>
                    <div className="flex-1 -mt-4 -mx-4">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="65%" data={radarData}>
                          <PolarGrid stroke="rgba(255,255,255,0.1)" />
                          <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                          <Radar name="Sinh viên" dataKey="value" stroke="#3b82f6" strokeWidth={2} fill="#3b82f6" fillOpacity={0.3} />
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: 'rgba(255,255,255,0.1)', fontSize: '12px' }} />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </motion.div>

                  {/* Ô 6: GHI CHÚ GVCN */}
                  <motion.div
                    className="md:col-span-3 md:row-span-1 glass-card p-5 group"
                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <StickyNote className="w-4 h-4 text-amber-400" />
                      <h3 className="text-slate-200 font-semibold text-sm">Ghi chú nhanh của GVCN</h3>
                    </div>
                    <textarea
                      className="w-full bg-navy-900/50 border border-white/10 rounded-xl p-3 text-sm text-slate-300
                                 focus:outline-none focus:ring-1 focus:ring-amber-500/50 resize-none h-12"
                      placeholder="Nhập ghi chú nhanh..."
                    />
                  </motion.div>

                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}