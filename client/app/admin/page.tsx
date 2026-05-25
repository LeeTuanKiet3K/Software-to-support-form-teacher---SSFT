'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, UserPlus, Copy, Check, ArrowRight, ArrowLeft } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

// Master passcode để truy cập trang admin (do chưa có tính năng đăng nhập riêng cho Super Admin)
const MASTER_PASSCODE = 'SSFT_Admin2026';

export default function AdminPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [passcode, setPasscode] = useState('');

  const [accountType, setAccountType] = useState<'advisor' | 'student'>('advisor');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [studentId, setStudentId] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successData, setSuccessData] = useState<{ email: string; temp_password: string } | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Nếu đã đăng nhập với quyền admin thì vào thẳng (phòng hờ tương lai có role admin)
    const role = sessionStorage.getItem('ssft_role');
    if (role === 'admin') {
      setIsAuthenticated(true);
    }
  }, []);

  const handleAuthenticate = (e: React.FormEvent) => {
    e.preventDefault();
    if (passcode === MASTER_PASSCODE) {
      setIsAuthenticated(true);
      setError('');
    } else {
      setError('Mã xác thực không chính xác!');
    }
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessData(null);

    if (!email || !fullName || (accountType === 'student' && !studentId)) {
      setError('Vui lòng nhập đầy đủ thông tin.');
      return;
    }

    setIsLoading(true);
    try {
      const endpoint = accountType === 'advisor' ? '/auth/advisors' : '/auth/students';
      const body = accountType === 'advisor'
        ? { advisor_email: email, advisor_name: fullName }
        : { student_email: email, student_name: fullName, student_id: studentId };

      const response = await apiClient(endpoint, {
        method: 'POST',
        body: JSON.stringify(body)
      });

      if (response.success) {
        setSuccessData({
          email: email,
          temp_password: response.temp_password
        });
        setEmail('');
        setFullName('');
        setStudentId('');
      }
    } catch (err: any) {
      setError(err.message || 'Có lỗi xảy ra khi tạo tài khoản.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (successData) {
      navigator.clipboard.writeText(`Email: ${successData.email}\nMật khẩu: ${successData.temp_password}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // ---------------------------------------------
  // Màn hình Yêu cầu Mã Xác thực Admin
  // ---------------------------------------------
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-navy-950">
        <motion.div
          className="w-full max-w-sm glass-card p-8"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center border border-red-500/30">
              <ShieldAlert className="w-8 h-8 text-red-500" />
            </div>
          </div>
          <h2 className="text-xl font-bold text-white text-center mb-2">Khu vực Quản trị</h2>
          <p className="text-slate-400 text-sm text-center mb-6">
            Vui lòng nhập mã xác thực quản trị viên để tiếp tục.
          </p>

          <form onSubmit={handleAuthenticate} className="space-y-4">
            <input
              type="password"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              className="input-dark text-center tracking-widest"
              placeholder="••••••••"
              autoFocus
            />
            {error && <p className="text-red-400 text-sm text-center">{error}</p>}
            <button type="submit" className="btn-primary w-full bg-red-600 hover:bg-red-500">
              Xác thực
            </button>
            <button
              type="button"
              onClick={() => router.push('/login')}
              className="w-full text-slate-400 text-sm hover:text-white flex items-center justify-center gap-2 mt-4"
            >
              <ArrowLeft className="w-4 h-4" /> Quay lại đăng nhập
            </button>
          </form>
        </motion.div>
      </div>
    );
  }

  // ---------------------------------------------
  // Màn hình Admin Dashboard (Tạo tài khoản)
  // ---------------------------------------------
  return (
    <div className="min-h-screen bg-navy-950 p-6 flex flex-col items-center">
      <div className="w-full max-w-2xl mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <ShieldAlert className="w-7 h-7 text-emerald-400" />
          Admin Dashboard
        </h1>
        <button
          onClick={() => router.push('/login')}
          className="px-4 py-2 bg-white/5 hover:bg-white/10 text-slate-300 rounded-lg transition-colors flex items-center gap-2 text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Thoát
        </button>
      </div>

      <motion.div
        className="w-full max-w-2xl glass-card p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-center gap-3 mb-6 pb-6 border-b border-white/10">
          <div className="p-3 bg-purple-500/20 rounded-xl">
            <UserPlus className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Tạo tài khoản mới</h2>
            <p className="text-sm text-slate-400">Cấp tài khoản cho Giáo viên hoặc Sinh viên</p>
          </div>
        </div>

        {/* Form chọn loại tài khoản */}
        <div className="flex bg-navy-900/50 p-1 rounded-xl mb-6">
          <button
            onClick={() => { setAccountType('advisor'); setSuccessData(null); setError(''); setStudentId(''); }}
            className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-colors ${accountType === 'advisor' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Giáo viên (Advisor)
          </button>
          <button
            onClick={() => { setAccountType('student'); setSuccessData(null); setError(''); setStudentId(''); }}
            className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-colors ${accountType === 'student' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Sinh viên (Student)
          </button>
        </div>

        <form onSubmit={handleCreateAccount} className="space-y-5">
          <div className="grid grid-cols-1 gap-5">
            {accountType === 'student' && (
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Mã số Sinh viên</label>
                <input
                  type="text"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  className="input-dark"
                  placeholder="MSSV"
                  disabled={isLoading}
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Họ và tên</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-dark"
                placeholder="Nguyễn Văn Mười"
                disabled={isLoading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-dark"
                placeholder={accountType === 'advisor' ? 'gvcn@hcmus.edu.vn' : 'mssv@student.hcmus.edu.vn'}
                disabled={isLoading}
              />
            </div>
          </div>

          {error && <p className="text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20">{error}</p>}

          <button
            type="submit"
            disabled={isLoading}
            className={`w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-medium text-white transition-all
              ${isLoading ? 'opacity-70 cursor-not-allowed' : 'hover:scale-[1.02] active:scale-[0.98]'}
              ${accountType === 'advisor' ? 'bg-purple-600 hover:bg-purple-500' : 'bg-blue-600 hover:bg-blue-500'}`}
          >
            {isLoading ? 'Đang khởi tạo...' : `Tạo tài khoản ${accountType === 'advisor' ? 'Giáo viên' : 'Sinh viên'}`}
            {!isLoading && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        {/* Hiển thị kết quả sau khi tạo thành công */}
        <AnimatePresence>
          {successData && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: 'auto', marginTop: 24 }}
              className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-5 overflow-hidden"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-emerald-400 font-medium flex items-center gap-2 mb-3">
                    <Check className="w-5 h-5" /> Tạo tài khoản thành công!
                  </h3>
                  <div className="space-y-1 text-sm">
                    <p className="text-slate-300"><span className="text-slate-500 w-24 inline-block">Email:</span> <strong className="text-white">{successData.email}</strong></p>
                    <p className="text-slate-300"><span className="text-slate-500 w-24 inline-block">Mật khẩu tạm:</span> <strong className="text-amber-400 text-base">{successData.temp_password}</strong></p>
                  </div>
                  <p className="text-xs text-slate-500 mt-4">
                    Vui lòng copy thông tin này gửi cho người dùng. Họ sẽ được yêu cầu đổi mật khẩu ở lần đăng nhập đầu tiên.
                  </p>
                </div>

                <button
                  onClick={copyToClipboard}
                  className="p-2 bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 rounded-lg transition-colors flex flex-col items-center"
                >
                  {copied ? <Check className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                  <span className="text-[10px] mt-1">{copied ? 'Đã copy' : 'Copy'}</span>
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </motion.div>
    </div>
  );
}
