'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  color: 'red' | 'amber' | 'blue' | 'emerald';
  delay?: number;
  trend?: string; // Ví dụ: "+2 so với tuần trước"
}

const colorMap = {
  red: {
    icon: 'text-red-400',
    bg: 'bg-red-500/10',
    glow: 'shadow-red-500/10',
    border: 'border-red-500/20',
    value: 'text-red-300',
  },
  amber: {
    icon: 'text-amber-400',
    bg: 'bg-amber-500/10',
    glow: 'shadow-amber-500/10',
    border: 'border-amber-500/20',
    value: 'text-amber-300',
  },
  blue: {
    icon: 'text-blue-400',
    bg: 'bg-blue-500/10',
    glow: 'shadow-blue-500/10',
    border: 'border-blue-500/20',
    value: 'text-blue-300',
  },
  emerald: {
    icon: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    glow: 'shadow-emerald-500/10',
    border: 'border-emerald-500/20',
    value: 'text-emerald-300',
  },
};

export function KpiCard({ title, value, icon: Icon, color, delay = 0, trend }: KpiCardProps) {
  const c = colorMap[color];

  return (
    <motion.div
      className={`glass-card p-5 border ${c.border} hover:border-opacity-40 transition-all duration-300`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: 'easeOut' }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-slate-400 text-sm font-medium truncate">{title}</p>
          <motion.p
            className={`text-4xl font-bold mt-2 ${c.value}`}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: delay + 0.2, type: 'spring', stiffness: 200 }}
          >
            {value}
          </motion.p>
          {trend && (
            <p className="text-xs text-slate-500 mt-1.5">{trend}</p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${c.bg} shrink-0`}>
          <Icon className={`w-6 h-6 ${c.icon}`} />
        </div>
      </div>
    </motion.div>
  );
}
