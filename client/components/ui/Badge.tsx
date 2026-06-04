'use client';

import type { IssuePriority, IssueStatus } from '@/types';
import { PRIORITY_LABELS, STATUS_LABELS } from '@/lib/mockData';
import { AlertTriangle, Flame, Minus, ChevronDown } from 'lucide-react';

// --- Priority Badge ---
const priorityConfig = {
  URGENT: { className: 'badge-urgent', icon: <AlertTriangle className="w-3 h-3" /> },
  HIGH:   { className: 'badge-high',   icon: <Flame className="w-3 h-3" /> },
  MEDIUM: { className: 'badge-medium', icon: <Minus className="w-3 h-3" /> },
  LOW:    { className: 'badge-low',    icon: <ChevronDown className="w-3 h-3" /> },
};

export function PriorityBadge({ priority }: { priority: IssuePriority | string }) {
  const config = priorityConfig[priority as IssuePriority] || priorityConfig['LOW'];
  const label = PRIORITY_LABELS[priority as IssuePriority] || priority;
  return (
    <span className={config.className}>
      {config.icon}
      {label}
    </span>
  );
}

// --- Status Badge ---
const statusConfig: Record<IssueStatus, { bg: string; text: string }> = {
  OPEN:             { bg: 'bg-red-500/10 border-red-500/30',     text: 'text-red-400' },
  IN_PROGRESS:      { bg: 'bg-blue-500/10 border-blue-500/30',   text: 'text-blue-400' },
  RESOLVED:         { bg: 'bg-emerald-500/10 border-emerald-500/30', text: 'text-emerald-400' },
  PENDING_ADVISOR:  { bg: 'bg-amber-500/10 border-amber-500/30', text: 'text-amber-400' },
};

export function StatusBadge({ status }: { status: IssueStatus | string }) {
  const cfg = statusConfig[status as IssueStatus] || statusConfig['OPEN'];
  const label = STATUS_LABELS[status as IssueStatus] || status;
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${cfg.bg} ${cfg.text}`}>
      {label}
    </span>
  );
}
