'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle, Clock, CheckCircle2, Users,
  Sparkles, RefreshCw, Key, LogOut, Bell, AlertCircle, X, Eye, EyeOff
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { KpiCard } from '@/components/KpiCard';
import { IssueTable } from '@/components/IssueTable';
import { IntentPieChart, WeeklyBarChart } from '@/components/StatsChart';
import { mockPieData, mockBarData } from '@/lib/mockData';
import { apiClient } from '@/lib/apiClient';
import type { Issue } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const [issues, setIssues] = useState<Issue[]>([]);
  const [stats, setStats] = useState({ urgent: 0, pending: 0, resolved: 0, totalStudents: 0 });
  const [resolvingId, setResolvingId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(true);
  const [advisorName, setAdvisorName] = useState('Giáo viên');
  const [advisorId, setAdvisorId] = useState('');

  // Password Modal State
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient('/dashboard/summary');
      setStats(data.stats || { urgent: 0, pending: 0, resolved: 0, totalStudents: 0 });
      setIssues(data.issues || []);
    } catch (error) {
      console.error("Lỗi lấy dữ liệu Dashboard:", error);
    } finally {
      setIsLoading(false);
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
          uid: advisorId,
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

  useEffect(() => {
    fetchDashboardData();
    if (typeof window !== 'undefined') {
      const name = sessionStorage.getItem('ssft_name');
      const uid = sessionStorage.getItem('ssft_id');
      if (name) setAdvisorName(name);
      if (uid) setAdvisorId(uid);

      const params = new URLSearchParams(window.location.search);
      if (params.get('action') === 'change-password') {
        setShowPasswordModal(true);
        // Optional: clear the param from URL
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  const handleResolve = async (issueId: string) => {
    try {
      setResolvingId(issueId);
      await apiClient(`/issues/${issueId}/resolve`, { method: 'POST' });
      await fetchDashboardData(); 
    } catch (error) {
      console.error("Lỗi giải quyết vấn đề:", error);
    } finally {
      setResolvingId(undefined);
    }
  };

  const activeIssues = issues.filter((i) => i.status !== 'RESOLVED');

  return (
    <div className="p-6 lg:p-8 space-y-8">
      {/* --- Header --- */}
      <motion.div
        className="flex items-start justify-between"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h1 className="text-2xl font-bold text-white">Dashboard GVCN</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Xin chào, <span className="text-slate-200 font-medium">{advisorName}</span> ·
            Lớp <span className="text-purple-300 font-medium">24CTT4</span> ·{' '}
            <span className="text-slate-500">{stats.totalStudents} sinh viên</span>
          </p>
        </div>
      </motion.div>

      {/* --- KPI Cards --- */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Khẩn cấp"
          value={stats.urgent}
          icon={AlertTriangle}
          color="red"
          delay={0}
          trend="Cần xử lý ngay"
        />
        <KpiCard
          title="Chờ xử lý"
          value={stats.pending}
          icon={Clock}
          color="amber"
          delay={0.1}
          trend={`${activeIssues.length} vấn đề đang mở`}
        />
        <KpiCard
          title="Đã giải quyết"
          value={stats.resolved}
          icon={CheckCircle2}
          color="emerald"
          delay={0.2}
          trend="Tháng này"
        />
        <KpiCard
          title="Tổng sinh viên"
          value={stats.totalStudents}
          icon={Users}
          color="blue"
          delay={0.3}
          trend="Lớp 24CTT4"
        />
      </div>

      {/* --- Main content: Issues + Charts --- */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <motion.div
          className="xl:col-span-2 space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.4 }}
        >
          <div className="flex items-center justify-between">
            <h2 className="text-slate-100 font-semibold text-lg">
              Vấn đề sinh viên
            </h2>
            <span className="text-xs text-slate-500 bg-navy-800/60 border border-white/[0.06]
                             px-3 py-1 rounded-full">
              {activeIssues.length} đang mở
            </span>
          </div>
          <IssueTable
            issues={issues}
            onResolve={handleResolve}
            isResolvingId={resolvingId}
          />
        </motion.div>

        <motion.div
          className="space-y-4"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
        >
          <h2 className="text-slate-100 font-semibold text-lg">Phân tích</h2>
          <IntentPieChart data={mockPieData} />
          <WeeklyBarChart data={mockBarData} />
        </motion.div>
      </div>
      
      {/* Password Modal */}
      <AnimatePresence>
        {showPasswordModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
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
                    <p className="text-red-400 text-sm flex items-center gap-2"><AlertCircle className="w-4 h-4"/> {passwordError}</p>
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
      </AnimatePresence>
    </div>
  );
}