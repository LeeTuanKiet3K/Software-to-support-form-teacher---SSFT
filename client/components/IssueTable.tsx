'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle2, ChevronRight, Clock, User, Brain, MessageSquare, Filter
} from 'lucide-react';
import type { Issue, IssuePriority, IssueStatus } from '@/types';
import { PriorityBadge, StatusBadge } from '@/components/ui/Badge';
import { INTENT_LABELS, SENTIMENT_LABELS } from '@/lib/mockData';

interface IssueTableProps {
  issues: Issue[];
  onResolve: (issueId: string) => void;
  isResolvingId?: string;
}

// Format thời gian tương đối (Relative time formatting)
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
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Lọc và sắp xếp
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

        {/* Status filter */}
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as IssueStatus | 'ALL')}
          className="bg-navy-800/80 border border-white/10 text-slate-300 text-sm
                     rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-purple-500/50"
        >
          <option value="ALL">Tất cả trạng thái</option>
          <option value="OPEN">Chờ xử lý</option>
          <option value="IN_PROGRESS">Đang xử lý</option>
          <option value="PENDING_ADVISOR">Chờ GVCN</option>
          <option value="RESOLVED">Đã giải quyết</option>
        </select>

        {/* Priority filter */}
        <select
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value as IssuePriority | 'ALL')}
          className="bg-navy-800/80 border border-white/10 text-slate-300 text-sm
                     rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-purple-500/50"
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
      <div className="space-y-3">
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
                className={`glass-card overflow-hidden transition-all duration-300
                  ${!issue.is_advisor_viewed && issue.status !== 'RESOLVED'
                    ? 'border-l-2 border-l-purple-500/60' : ''}`}
              >
                {/* --- Issue Header (luôn hiển thị) --- */}
                <button
                  onClick={() => setExpandedId(expandedId === issue.id ? null : issue.id)}
                  className="w-full p-4 flex items-center gap-4 text-left hover:bg-white/[0.02] transition-colors"
                >
                  {/* Avatar */}
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500/30 to-blue-500/30
                                  border border-purple-500/20 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-slate-300" />
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-slate-100 font-medium text-sm truncate">
                        {issue.student_id}
                      </span>
                      {!issue.is_advisor_viewed && issue.status !== 'RESOLVED' && (
                        <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse shrink-0" />
                      )}
                    </div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <PriorityBadge priority={issue.priority} />
                      <StatusBadge status={issue.status} />
                    </div>
                  </div>

                  {/* Time + expand */}
                  <div className="text-right shrink-0">
                    <div className="flex items-center gap-1 text-slate-500 text-xs mb-1">
                      <Clock className="w-3 h-3" />
                      {formatRelativeTime(issue.created_at)}
                    </div>
                    <ChevronRight
                      className={`w-4 h-4 text-slate-500 ml-auto transition-transform duration-200
                                  ${expandedId === issue.id ? 'rotate-90' : ''}`}
                    />
                  </div>
                </button>

                {/* --- Expanded Detail --- */}
                <AnimatePresence>
                  {expandedId === issue.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.25 }}
                      className="overflow-hidden"
                    >
                      <div className="px-4 pb-4 border-t border-white/[0.05] pt-4 space-y-4">
                        {/* AI Analysis */}
                        <div className="grid grid-cols-2 gap-3">
                          <div className="bg-navy-900/60 rounded-xl p-3">
                            <div className="flex items-center gap-2 mb-1.5">
                              <Brain className="w-3.5 h-3.5 text-purple-400" />
                              <span className="text-xs text-slate-400 font-medium">Phân tích AI</span>
                            </div>
                            <p className="text-sm text-slate-200 font-medium">
                              {INTENT_LABELS[issue.intent]}
                            </p>
                          </div>
                          <div className="bg-navy-900/60 rounded-xl p-3">
                            <div className="flex items-center gap-2 mb-1.5">
                              <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
                              <span className="text-xs text-slate-400 font-medium">Cảm xúc</span>
                            </div>
                            <p className="text-sm text-slate-200 font-medium">
                              {SENTIMENT_LABELS[issue.sentiment]}
                            </p>
                          </div>
                        </div>

                        {/* Action */}
                        {issue.status !== 'RESOLVED' && (
                          <button
                            onClick={() => onResolve(issue.id)}
                            disabled={isResolvingId === issue.id}
                            className="btn-primary w-full flex items-center justify-center gap-2 py-2.5
                                       disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            {isResolvingId === issue.id ? (
                              <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Đang xử lý...
                              </>
                            ) : (
                              <>
                                <CheckCircle2 className="w-4 h-4" />
                                Đánh dấu Đã giải quyết
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
