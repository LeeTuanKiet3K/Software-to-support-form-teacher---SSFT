'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileSpreadsheet, Search, Filter, Download, MoreHorizontal, CheckCircle2 } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

export default function AcademicPage() {
  const [grades, setGrades] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [classId, setClassId] = useState('');

  useEffect(() => {
    const fetchGrades = async () => {
      try {
        setIsLoading(true);
        const storedClassId = sessionStorage.getItem('ssft_class_id');
        if (!storedClassId) {
          setGrades([]);
          setIsLoading(false);
          return;
        }
        setClassId(storedClassId);
        const data = await apiClient(`/academic/class/${storedClassId}/grades`);
        setGrades(data || []);
      } catch (error) {
        console.error("Lỗi tải điểm:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchGrades();
  }, []);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await uploadFile(e.target.files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(10);
    
    // Tạo hiệu ứng % chạy mượt mà trong lúc chờ Backend
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => (prev < 85 ? prev + 15 : prev));
    }, 400);

    const formData = new FormData();
    formData.append('file', file);
    if (classId) {
      formData.append('class_id', classId);
    }

    try {
      await apiClient('/academic/grades/upload', {
        method: 'POST',
        body: formData as unknown as BodyInit,
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Reload lại danh sách điểm
      if (classId) {
        const newData = await apiClient(`/academic/class/${classId}/grades`);
        setGrades(newData || []);
      }
      
    } catch (error) {
      console.error("Lỗi upload file:", error);
      clearInterval(progressInterval);
    } finally {
      setTimeout(() => setIsUploading(false), 500);
    }
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Quản lý Học vụ</h1>
          <p className="text-slate-400 text-sm">{classId ? `Cập nhật điểm số và theo dõi kết quả học tập của lớp ${classId}` : 'Bạn chưa được phân công lớp chủ nhiệm.'}</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-ghost flex items-center gap-2 text-sm bg-navy-800 border-white/10">
            <Download className="w-4 h-4" />
            Tải File Mẫu
          </button>
          <button className="btn-primary flex items-center gap-2 text-sm" onClick={() => window.location.reload()}>
            Đồng bộ từ Hệ thống
          </button>
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <motion.div
        className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 overflow-hidden
                    ${isDragging ? 'border-purple-500 bg-purple-500/10' : 'border-white/10 bg-navy-900/50 hover:bg-navy-800/50 hover:border-white/20'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="p-10 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 rounded-full bg-navy-800 flex items-center justify-center mb-4 shadow-lg border border-white/5">
            <UploadCloud className={`w-8 h-8 ${isDragging ? 'text-purple-400' : 'text-slate-400'}`} />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Kéo thả file bảng điểm vào đây</h3>
          <p className="text-slate-400 text-sm mb-6 max-w-md">
            Hỗ trợ định dạng Excel (.xlsx, .xls) hoặc CSV. Hệ thống AI sẽ tự động phân tích và gắn thẻ sinh viên có nguy cơ rớt môn.
          </p>
          <label className="cursor-pointer px-5 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm font-medium text-white transition-colors">
            <span>Chọn file từ máy tính</span>
            <input type="file" className="hidden" accept=".xlsx, .xls, .csv" onChange={handleFileSelect} />
          </label>
        </div>

        {/* Upload Progress Overlay */}
        <AnimatePresence>
          {isUploading && (
            <motion.div
              className="absolute inset-0 bg-navy-900/90 backdrop-blur-sm flex flex-col items-center justify-center px-10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <FileSpreadsheet className="w-10 h-10 text-emerald-400 mb-4 animate-bounce" />
              <h3 className="text-white font-semibold mb-4">Đang phân tích dữ liệu...</h3>
              <div className="w-full max-w-md bg-navy-950 rounded-full h-2 overflow-hidden border border-white/5">
                <motion.div
                  className="h-full bg-gradient-to-r from-emerald-500 to-blue-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 mt-3">{uploadProgress}% Hoàn tất</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Data Table */}
      <motion.div
        className="glass-card overflow-hidden flex flex-col"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="p-5 border-b border-white/5 flex flex-wrap items-center justify-between gap-4 bg-navy-800/30">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Tìm MSSV, tên..."
                className="bg-navy-950/50 border border-white/10 text-sm text-white placeholder-slate-500 rounded-lg pl-9 pr-4 py-2 focus:outline-none focus:border-purple-500/50 w-64"
              />
            </div>
            <button className="p-2 border border-white/10 rounded-lg text-slate-400 hover:bg-white/5 hover:text-white transition-colors">
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-navy-900/50 text-slate-400 border-b border-white/5">
              <tr>
                <th className="px-6 py-4 font-medium w-10"><input type="checkbox" className="rounded border-white/20 bg-navy-800" /></th>
                <th className="px-6 py-4 font-medium">MSSV</th>
                <th className="px-6 py-4 font-medium">Họ và Tên</th>
                <th className="px-6 py-4 font-medium text-right">GPA Hệ 4</th>
                <th className="px-6 py-4 font-medium text-center">Tình trạng</th>
                <th className="px-6 py-4 font-medium text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                 <tr><td colSpan={6} className="text-center py-8 text-slate-400">Đang tải dữ liệu...</td></tr>
              ) : !classId ? (
                 <tr><td colSpan={6} className="text-center py-8 text-slate-400">Không có dữ liệu vì bạn chưa được gán lớp.</td></tr>
              ) : grades.length === 0 ? (
                 <tr><td colSpan={6} className="text-center py-8 text-slate-400">Chưa có dữ liệu. Vui lòng tải file lên.</td></tr>
              ) : grades.map((student, idx) => (
                <tr key={student.student_id || idx} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="px-6 py-4"><input type="checkbox" className="rounded border-white/20 bg-navy-800" /></td>
                  <td className="px-6 py-4 text-slate-300 font-medium">{student.student_id}</td>
                  <td className="px-6 py-4 text-white font-semibold">{student.name || 'Chưa cập nhật'}</td>
                  <td className="px-6 py-4 text-right text-purple-400 font-bold">{Number(student.gpa).toFixed(2)}</td>
                  <td className="px-6 py-4 text-center">
                    {(() => {
                      let status = "An toàn";
                      let colorClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                      
                      if (!student.gpa || student.gpa === 0) {
                        status = "Chưa có điểm";
                        colorClass = "bg-slate-500/10 text-slate-400 border-slate-500/20";
                      } else if (student.gpa < 2.0) {
                        status = "Nguy cơ";
                        colorClass = "bg-red-500/10 text-red-400 border-red-500/20";
                      } else if (student.gpa < 2.5) {
                        status = "Cảnh báo";
                        colorClass = "bg-orange-500/10 text-orange-400 border-orange-500/20";
                      }

                      return (
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${colorClass}`}>
                          {status}
                        </span>
                      );
                    })()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="p-1.5 text-slate-500 hover:text-white rounded-md hover:bg-white/10 transition-colors">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}