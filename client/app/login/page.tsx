'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { GraduationCap, Mail, Lock, ArrowRight, AlertCircle, Eye, EyeOff, User, X, Info, ShieldCheck } from 'lucide-react';
import { api } from '@/lib/api';

type LoginType = 'advisor' | 'student';

export default function LoginPage() {
  const router = useRouter();
  const [loginType, setLoginType] = useState<LoginType>('student');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState<'about' | 'policy' | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!identifier || !password) {
      setError('Vui lòng nhập đầy đủ thông tin.');
      return;
    }
    
    if (loginType === 'advisor') {
      if (!identifier.endsWith('@hcmus.edu.vn') && !identifier.endsWith('@fit.hcmus.edu.vn')) {
        setError('Email giảng viên phải có đuôi @hcmus.edu.vn hoặc @fit.hcmus.edu.vn');
        return;
      }
    } else {
      if (!/^2\d{7}$/.test(identifier)) {
        setError('MSSV phải gồm đúng 8 chữ số và bắt đầu bằng số 2.');
        return;
      }
    }

    if (password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự.');
      return;
    }

    setIsLoading(true);

    setIsLoading(true);

    try {
      const res = await api.login(identifier, password);
      if (res.success) {
        sessionStorage.setItem('ssft_role', res.profile?.role || loginType);
        sessionStorage.setItem('ssft_id', res.profile?.uid || identifier);
        
        setIsLoading(false);

        if (loginType === 'advisor') {
          router.push('/dashboard');
        } else {
          router.push('/student');
        }
      } else {
        setError(res.error || 'Đăng nhập thất bại');
        setIsLoading(false);
      }
    } catch (err: any) {
      setError(err.message || 'Lỗi kết nối máy chủ');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden px-4">
      {/* --- Nền gradient động (Animated background blobs) --- */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 rounded-full blur-3xl opacity-20"
          style={{ background: 'radial-gradient(circle, #7c3aed, transparent)', top: '-10%', left: '-5%' }}
          animate={{ scale: [1, 1.2, 1], rotate: [0, 45, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute w-80 h-80 rounded-full blur-3xl opacity-15"
          style={{ background: 'radial-gradient(circle, #3b82f6, transparent)', bottom: '-10%', right: '-5%' }}
          animate={{ scale: [1.2, 1, 1.2], rotate: [45, 0, 45] }}
          transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute w-64 h-64 rounded-full blur-3xl opacity-10"
          style={{ background: 'radial-gradient(circle, #7c3aed, #3b82f6)', top: '50%', left: '60%' }}
          animate={{ x: [-20, 20, -20], y: [-20, 20, -20] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      {/* --- Login Card --- */}
      <motion.div
        className="w-full max-w-md relative z-10"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        {/* Logo & Title */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4
                          bg-gradient-to-br from-purple-600 to-blue-500
                          shadow-glow-purple">
            <GraduationCap className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight px-4 leading-snug">
            Hệ thống Hỗ trợ Giáo viên Chủ nhiệm
          </h1>
          <p className="text-slate-400 mt-2 text-sm font-medium">
            Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM
          </p>
        </motion.div>

        {/* Card Form */}
        <motion.div
          className="glass-card p-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          {/* Tabs */}
          <div className="flex bg-navy-900/50 p-1 rounded-xl mb-6 relative">
            <div 
              className={`absolute top-1 bottom-1 w-[calc(50%-4px)] bg-purple-600 rounded-lg transition-all duration-300 ease-out shadow-lg
                         ${loginType === 'student' ? 'left-1' : 'left-[calc(50%+2px)]'}`}
            />
            <button
              type="button"
              onClick={() => { setLoginType('student'); setError(''); setIdentifier(''); }}
              className={`flex-1 py-2.5 text-sm font-medium rounded-lg relative z-10 transition-colors duration-300
                         ${loginType === 'student' ? 'text-white' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Sinh viên
            </button>
            <button
              type="button"
              onClick={() => { setLoginType('advisor'); setError(''); setIdentifier(''); }}
              className={`flex-1 py-2.5 text-sm font-medium rounded-lg relative z-10 transition-colors duration-300
                         ${loginType === 'advisor' ? 'text-white' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Giáo viên
            </button>
          </div>

          <h2 className="text-xl font-semibold text-white mb-1">
            Đăng nhập {loginType === 'advisor' ? 'Hệ thống Quản trị' : 'Cổng Sinh viên'}
          </h2>
          <p className="text-slate-400 text-sm mb-6">
            {loginType === 'advisor' 
              ? 'Sử dụng email do trường cấp (@hcmus.edu.vn)' 
              : 'Sử dụng Mã số Sinh viên (MSSV) của bạn'}
          </p>

          <form onSubmit={handleLogin} className="space-y-5">
            {/* Identifier (Email / MSSV) */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                {loginType === 'advisor' ? 'Địa chỉ Email' : 'Mã số Sinh viên (MSSV)'}
              </label>
              <div className="relative">
                {loginType === 'advisor' ? (
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 w-[18px] h-[18px]" />
                ) : (
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 w-[18px] h-[18px]" />
                )}
                <input
                  type={loginType === 'advisor' ? 'email' : 'text'}
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  className="input-dark pl-11"
                  placeholder={loginType === 'advisor' ? 'email@hcmus.edu.vn' : 'VD: 24120101'}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Mật khẩu
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 w-[18px] h-[18px]" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-dark pl-11 pr-11"
                  placeholder="••••••••"
                  autoComplete="current-password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
                </button>
              </div>
            </div>

            {/* Error message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="flex items-center gap-2.5 bg-red-500/10 border border-red-500/30
                             rounded-xl px-4 py-3 text-red-400 text-sm overflow-hidden"
                >
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex items-center justify-center gap-2 mt-2
                         disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Đang xác thực...
                </>
              ) : (
                <>
                  Đăng nhập
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </motion.div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-xs text-slate-600 mb-2">
            Được thực hiện bởi Nhóm 8 - 24CTT4, HCMUS
          </p>
          <div className="flex items-center justify-center gap-3 text-xs text-slate-500">
            <button onClick={() => setShowModal('about')} className="hover:text-purple-400 transition-colors">Về hệ thống</button>
            <span>•</span>
            <button onClick={() => setShowModal('policy')} className="hover:text-purple-400 transition-colors">Bảo mật & Điều khoản</button>
          </div>
        </div>
      </motion.div>

      {/* --- Modal (Pop-up) --- */}
      <AnimatePresence>
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              className="absolute inset-0 bg-navy-950/80 backdrop-blur-sm"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              onClick={() => setShowModal(null)}
            />
            <motion.div 
              className="relative w-full max-w-lg bg-navy-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]"
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            >
              {/* Header Modal */}
              <div className="flex items-center justify-between p-5 border-b border-white/5 bg-navy-800/50">
                <div className="flex items-center gap-2">
                  {showModal === 'about' ? <Info className="w-5 h-5 text-purple-400" /> : <ShieldCheck className="w-5 h-5 text-emerald-400" />}
                  <h3 className="text-white font-semibold">
                    {showModal === 'about' ? 'Về hệ thống HTHT GVCN' : 'Chính sách Bảo mật & Điều khoản'}
                  </h3>
                </div>
                <button onClick={() => setShowModal(null)} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Body Modal */}
              <div className="p-6 overflow-y-auto custom-scrollbar text-sm text-slate-300 leading-relaxed space-y-4">
                {showModal === 'about' ? (
                  <>
                    <p>
                      <strong className="text-white">Hệ thống Hỗ trợ Giáo viên Chủ nhiệm (HTHT GVCN)</strong> là một giải pháp chuyển đổi số toàn diện nhằm nâng cao hiệu quả quản lý, tư vấn và hỗ trợ sinh viên tại Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM.
                    </p>
                    <div className="bg-purple-500/10 border border-purple-500/20 p-4 rounded-xl">
                      <p className="text-purple-300 font-medium mb-2">Điểm nổi bật của Trợ lý AI:</p>
                      <ul className="list-disc list-inside space-y-2 text-purple-200/80">
                        <li><strong>Đa mô hình (Multi-model):</strong> Kết hợp sức mạnh suy luận logic của <span className="text-purple-300">Gemini</span> và khả năng xử lý ngôn ngữ mượt mà của <span className="text-purple-300">Llama 3</span>.</li>
                        <li><strong>Đọc vị Cảm xúc (Sentiment Analysis):</strong> Tự động nhận diện mức độ căng thẳng qua từng câu chat để phát hiện sớm các khủng hoảng tâm lý của sinh viên.</li>
                        <li><strong>Trợ lý Quyết định (Decision Support):</strong> Tự động tổng hợp điểm số, đánh giá chuyên cần và tự động phác thảo cảnh báo học vụ cho Giáo viên.</li>
                      </ul>
                    </div>
                    <p>Sản phẩm được phát triển bởi <strong>Nhóm 8 - Lớp 24CTT4</strong> với mục tiêu mang lại trải nghiệm tối ưu nhất cho cả Giáo viên và Sinh viên.</p>
                  </>
                ) : (
                  <>
                    <p>
                      Bằng việc đăng nhập vào hệ thống, bạn đồng ý với các điều khoản bảo mật sau:
                    </p>
                    <div className="space-y-3 mt-2">
                      <div className="bg-navy-800 p-3 rounded-lg border border-white/5">
                        <strong className="text-white block mb-1">1. Quyền riêng tư dữ liệu chat</strong>
                        Toàn bộ nội dung trò chuyện giữa sinh viên và Trợ lý AI được mã hóa an toàn. Chỉ Giáo viên Chủ nhiệm (GVCN) được cấp quyền mới có thể xem các bản phân tích nguy cơ dựa trên các đoạn hội thoại này.
                      </div>
                      <div className="bg-navy-800 p-3 rounded-lg border border-white/5">
                        <strong className="text-white block mb-1">2. Trách nhiệm của AI</strong>
                        Trợ lý AI chỉ đóng vai trò phân tích dữ liệu và đưa ra lời khuyên tham khảo. Các quyết định liên quan đến học vụ, tâm lý sinh viên hoàn toàn phụ thuộc vào sự đánh giá cuối cùng của GVCN.
                      </div>
                      <div className="bg-navy-800 p-3 rounded-lg border border-white/5">
                        <strong className="text-white block mb-1">3. Lưu trữ dữ liệu</strong>
                        Hệ thống tuân thủ nghiêm ngặt các quy định về bảo vệ dữ liệu giáo dục. Thông tin sinh viên không được chia sẻ cho bất kỳ bên thứ ba nào nằm ngoài máy chủ của Trường Đại học.
                      </div>
                    </div>
                  </>
                )}
              </div>

              {/* Footer Modal */}
              <div className="p-4 border-t border-white/5 bg-navy-800/30 text-right">
                <button onClick={() => setShowModal(null)} className="px-5 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-xl transition-colors">
                  Tôi đã hiểu
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
