'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle2, Clock, User, Brain, MessageSquare, Filter, X, Send, Phone, Mail
} from 'lucide-react';
import type { Issue, IssuePriority, IssueStatus } from '@/types';
import { PriorityBadge, StatusBadge } from '@/components/ui/Badge';
import { INTENT_LABELS, SENTIMENT_LABELS } from '@/lib/mockData';

interface IssueTableProps {
  issues: Issue[];
  onResolve: (issueId: string) => void;
  isResolvingId?: string;
}

function formatRelativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins} phút trước`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} giờ trước`;
  return `${Math.floor(hrs / 24)} ngày trước`;
}

const priorityOrder: Record<IssuePriority, number> = {
  URGENT: 0, HIGH: 1, MEDIUM: 2, LOW: 3,
};

export function IssueTable({ issues, onResolve, isResolvingId }: IssueTableProps) {
  const [filterStatus, setFilterStatus] = useState<IssueStatus | 'ALL'>('ALL');
  const [filterPriority, setFilterPriority] = useState<IssuePriority | 'ALL'>('ALL');
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);

  const filtered = issues
    .filter((i) => filterStatus === 'ALL' || i.status === filterStatus)
    .filter((i) => filterPriority === 'ALL' || i.priority === filterPriority)
    .sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  return (
    <div className="space-y-4">
      {/* --- Filter Bar --- */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-slate-400">
          <Filter className="w-4 h-4" />
          <span className="text-sm font-medium">Lọc:</span>
        </div>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as IssueStatus | 'ALL')}
          className="bg-navy-800/80 border border-white/10 text-slate-300 text-sm
                     rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-purple-500/50 transition-colors hover:bg-navy-700/80 cursor-pointer"
        >
          <option value="ALL">Tất cả trạng thái</option>
          <option value="OPEN">Chờ xử lý</option>
          <option value="IN_PROGRESS">Đang xử lý</option>
          <option value="PENDING_ADVISOR">Chờ GVCN</option>
          <option value="RESOLVED">Đã giải quyết</option>
        </select>

        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value as IssuePriority | 'ALL')}
          className="bg-navy-800/80 border border-white/10 text-slate-300 text-sm
                     rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-purple-500/50 transition-colors hover:bg-navy-700/80 cursor-pointer"
        >
          <option value="ALL">Tất cả mức độ</option>
          <option value="URGENT">Khẩn cấp</option>
          <option value="HIGH">Ưu tiên cao</option>
          <option value="MEDIUM">Trung bình</option>
          <option value="LOW">Thấp</option>
        </select>

        <span className="text-xs text-slate-500 ml-auto">
          {filtered.length} vấn đề
        </span>
      </div>

      {/* --- Issue List --- */}
      <div className="space-y-3 relative">
        <AnimatePresence mode="popLayout">
          {filtered.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card p-12 text-center"
            >
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
              <p className="text-slate-300 font-medium">Không có vấn đề nào</p>
              <p className="text-slate-500 text-sm mt-1">Lớp học đang ổn định!</p>
            </motion.div>
          ) : (
            filtered.map((issue, idx) => (
              <motion.div
                key={issue.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: idx * 0.05, duration: 0.3 }}
                className={`glass-card overflow-hidden transition-all duration-300 cursor-pointer hover:border-purple-500/30 hover:bg-white/[0.03] hover:shadow-[0_0_15px_rgba(168,85,247,0.1)] hover:-translate-y-0.5
                  ${!issue.is_advisor_viewed && issue.status !== 'RESOLVED'
                    ? 'border-l-2 border-l-purple-500/60' : ''}`}
                onClick={() => setSelectedIssue(issue)}
              >
                <div className="w-full p-4 flex items-center gap-4 text-left">
                  {/* Avatar */}
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500/30 to-blue-500/30
                                  border border-purple-500/20 flex items-center justify-center shrink-0 shadow-inner">
                    <User className="w-5 h-5 text-slate-300" />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-slate-100 font-semibold text-sm truncate">
                        {issue.student_id}
                      </span>
                      {!issue.is_advisor_viewed && issue.status !== 'RESOLVED' && (
                        <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse shrink-0 shadow-[0_0_8px_#a855f7]" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <PriorityBadge priority={issue.priority} />
                      <StatusBadge status={issue.status} />
                      <span className="text-xs text-slate-400 truncate max-w-[200px] hidden sm:inline-block ml-2 border-l border-white/10 pl-2">
                        {issue.content}
                      </span>
                    </div>
                  </div>

                  {/* Time */}
                  <div className="text-right shrink-0">
                    <div className="flex items-center gap-1 text-slate-500 text-xs font-medium">
                      <Clock className="w-3.5 h-3.5" />
                      {formatRelativeTime(issue.created_at)}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* --- Slide-over Modal --- */}
      <AnimatePresence>
        {selectedIssue && (
          <>
            <motion.div
              className="fixed inset-0 bg-navy-950/60 backdrop-blur-sm z-40"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedIssue(null)}
            />
            <motion.div
              className="fixed top-0 right-0 w-full max-w-md h-full bg-navy-900 border-l border-white/10 shadow-2xl z-50 flex flex-col"
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', bounce: 0, duration: 0.4 }}
            >
              {/* Header Modal */}
              <div className="flex items-center justify-between p-5 border-b border-white/10 bg-navy-800/50 backdrop-blur-md">
                <h2 className="text-lg font-semibold text-white">Chi tiết vấn đề</h2>
                <button
                  onClick={() => setSelectedIssue(null)}
                  className="p-2 text-slate-400 hover:text-white rounded-full hover:bg-white/5 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Body Modal */}
              <div className="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar">
                {/* Student Info */}
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-500/40 to-blue-500/40 border border-purple-500/30 flex items-center justify-center p-1">
                    <div className="w-full h-full bg-navy-900 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-slate-300" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg">{selectedIssue.student_id}</h3>
                    <p className="text-slate-400 text-sm">Khoa Công nghệ Thông tin</p>
                    <div className="flex gap-2 mt-2">
                      <PriorityBadge priority={selectedIssue.priority} />
                      <StatusBadge status={selectedIssue.status} />
                    </div>
                  </div>
                </div>

                {/* AI Analysis Cards */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gradient-to-br from-navy-800 to-navy-900 border border-white/5 rounded-xl p-4 shadow-inner relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-16 h-16 bg-purple-500/10 rounded-full blur-xl group-hover:bg-purple-500/20 transition-all"></div>
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="w-4 h-4 text-purple-400" />
                      <span className="text-xs text-slate-400 font-medium">Phân tích AI</span>
                    </div>
                    <p className="text-sm text-slate-100 font-medium">
                      {INTENT_LABELS[selectedIssue.intent]}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-navy-800 to-navy-900 border border-white/5 rounded-xl p-4 shadow-inner relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-16 h-16 bg-blue-500/10 rounded-full blur-xl group-hover:bg-blue-500/20 transition-all"></div>
                    <div className="flex items-center gap-2 mb-2">
                      <MessageSquare className="w-4 h-4 text-blue-400" />
                      <span className="text-xs text-slate-400 font-medium">Cảm xúc</span>
                    </div>
                    <p className="text-sm text-slate-100 font-medium">
                      {SENTIMENT_LABELS[selectedIssue.sentiment]}
                    </p>
                  </div>
                </div>

                {/* Issue Content */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                    Nội dung sinh viên phản ánh
                  </h4>
                  <div className="bg-navy-950 border border-white/5 rounded-xl p-4 text-sm text-slate-300 leading-relaxed italic border-l-2 border-l-blue-500">
                    "{selectedIssue.content}"
                  </div>
                </div>

                {/* Quick Actions */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-300 mb-3">Thao tác nhanh</h4>
                  <div className="flex gap-2">
                    <button className="flex-1 flex flex-col items-center gap-2 p-3 bg-navy-800 border border-white/5 rounded-xl hover:bg-navy-700 transition-colors group">
                      <div className="p-2 bg-blue-500/10 rounded-full text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                        <Send className="w-4 h-4" />
                      </div>
                      <span className="text-xs text-slate-300">Phản hồi</span>
                    </button>
                    <button className="flex-1 flex flex-col items-center gap-2 p-3 bg-navy-800 border border-white/5 rounded-xl hover:bg-navy-700 transition-colors group">
                      <div className="p-2 bg-emerald-500/10 rounded-full text-emerald-400 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                        <Phone className="w-4 h-4" />
                      </div>
                      <span className="text-xs text-slate-300">Gọi điện</span>
                    </button>
                    <button className="flex-1 flex flex-col items-center gap-2 p-3 bg-navy-800 border border-white/5 rounded-xl hover:bg-navy-700 transition-colors group">
                      <div className="p-2 bg-purple-500/10 rounded-full text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-colors">
                        <Mail className="w-4 h-4" />
                      </div>
                      <span className="text-xs text-slate-300">Email</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Footer Modal */}
              <div className="p-5 border-t border-white/10 bg-navy-900">
                {selectedIssue.status !== 'RESOLVED' ? (
                  <button
                    onClick={() => {
                      onResolve(selectedIssue.id);
                      setSelectedIssue(null);
                    }}
                    disabled={isResolvingId === selectedIssue.id}
                    className="btn-primary w-full flex items-center justify-center gap-2 py-3 rounded-xl
                               disabled:opacity-60 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(168,85,247,0.3)] hover:shadow-[0_0_25px_rgba(168,85,247,0.5)] transition-all"
                  >
                    {isResolvingId === selectedIssue.id ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Đang xử lý...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-5 h-5" />
                        Đánh dấu Đã xử lý xong
                      </>
                    )}
                  </button>
                ) : (
                  <button
                    disabled
                    className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  >
                    <CheckCircle2 className="w-5 h-5" />
                    Đã giải quyết
                  </button>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
