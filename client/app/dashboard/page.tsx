'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle, Clock, CheckCircle2, Users,
  Sparkles, RefreshCw,
} from 'lucide-react';
import { KpiCard } from '@/components/KpiCard';
import { IssueTable } from '@/components/IssueTable';
import { IntentPieChart, WeeklyBarChart } from '@/components/StatsChart';
import { mockPieData, mockBarData } from '@/lib/mockData';
import { apiClient } from '@/lib/apiClient';
import type { Issue } from '@/types';

export default function DashboardPage() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [stats, setStats] = useState({ urgent: 0, pending: 0, resolved: 0, totalStudents: 0 });
  const [resolvingId, setResolvingId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(true);

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

  useEffect(() => {
    fetchDashboardData();
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
          <p className="text-slate-400 text-sm">
            Xin chào, <span className="text-slate-200 font-medium">ThS. Nguyễn Thị Lan</span> ·
            Lớp <span className="text-purple-300 font-medium">24CTT4</span> ·{' '}
            <span className="text-slate-500">{stats.totalStudents} sinh viên</span>
          </p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="btn-ghost flex items-center gap-2 text-sm"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          Làm mới
        </button>
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
        {/* Issue Table - chiếm 2/3 */}
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

        {/* Charts - chiếm 1/3 */}
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
    </div>
  );
}