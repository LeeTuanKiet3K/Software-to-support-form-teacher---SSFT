'use client';

import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import type { PieChartData, BarChartData } from '@/types';

// --- Custom Tooltip --- 
const CustomTooltip = ({ active, payload, label }: {
  active?: boolean; payload?: { name: string; value: number; color: string }[]; label?: string;
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-navy-900 border border-white/10 rounded-xl p-3 shadow-card">
      {label && <p className="text-slate-300 text-xs font-medium mb-2">{label}</p>}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-400">{p.name}:</span>
          <span className="text-white font-semibold">{p.value}</span>
        </div>
      ))}
    </div>
  );
};

// --- Pie Chart: Phân loại theo Intent ---
export function IntentPieChart({ data }: { data: PieChartData[] }) {
  return (
    <div className="glass-card p-5">
      <h3 className="text-slate-200 font-semibold mb-1">Phân loại vấn đề</h3>
      <p className="text-slate-500 text-xs mb-4">Theo loại yêu cầu của sinh viên</p>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} stroke="rgba(255,255,255,0.05)" strokeWidth={1} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span style={{ color: '#94a3b8', fontSize: '12px' }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

// --- Bar Chart: Xu hướng theo tuần ---
export function WeeklyBarChart({ data }: { data: BarChartData[] }) {
  return (
    <div className="glass-card p-5">
      <h3 className="text-slate-200 font-semibold mb-1">Xu hướng theo tuần</h3>
      <p className="text-slate-500 text-xs mb-4">Số lượng vấn đề phân theo mức độ</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} barSize={10} barGap={2}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" vertical={false} />
          <XAxis
            dataKey="week"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={25}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar dataKey="urgent" name="Khẩn cấp" fill="#ef4444" radius={[4, 4, 0, 0]} />
          <Bar dataKey="high"   name="Cao"       fill="#f59e0b" radius={[4, 4, 0, 0]} />
          <Bar dataKey="medium" name="Trung bình" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          <Bar dataKey="low"    name="Thấp"      fill="#10b981" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
