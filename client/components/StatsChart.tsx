'use client';

import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import type { PieChartData, BarChartData } from '@/types';

// --- Custom Tooltip --- 
const CustomTooltip = ({ active, payload, label }: {
  active?: boolean; payload?: { name: string; value: number; color: string; payload?: any }[]; label?: string;
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-navy-900/90 backdrop-blur-md border border-white/10 rounded-xl p-3 shadow-2xl">
      {label && <p className="text-slate-300 text-xs font-semibold mb-2">{label}</p>}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 text-xs my-1">
          <div className="w-2.5 h-2.5 rounded-full shadow-sm" style={{ background: p.color || (p.payload && p.payload.fill) || '#fff' }} />
          <span className="text-slate-400">{p.name}:</span>
          <span className="text-white font-bold">{p.value}</span>
        </div>
      ))}
    </div>
  );
};

// --- Pie Chart: Phân loại theo Intent ---
export function IntentPieChart({ data }: { data: PieChartData[] }) {
  return (
    <div className="glass-card p-5 hover:shadow-lg transition-shadow duration-300 relative overflow-hidden group">
      <div className="absolute -right-10 -top-10 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl group-hover:bg-purple-500/20 transition-all duration-500" />
      <h3 className="text-slate-200 font-semibold mb-1">Phân loại vấn đề</h3>
      <p className="text-slate-500 text-xs mb-4">Theo loại yêu cầu của sinh viên</p>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <defs>
            {data.map((entry, index) => (
              <linearGradient key={`grad-${index}`} id={`pieGrad-${index}`} x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor={entry.color} stopOpacity={1} />
                <stop offset="100%" stopColor={entry.color} stopOpacity={0.6} />
              </linearGradient>
            ))}
          </defs>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={4}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={`url(#pieGrad-${index})`} style={{ filter: 'drop-shadow(0px 2px 4px rgba(0,0,0,0.2))' }} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span className="text-slate-400 text-xs ml-1">{value}</span>
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
    <div className="glass-card p-5 hover:shadow-lg transition-shadow duration-300 relative overflow-hidden group">
      <div className="absolute -left-10 -bottom-10 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all duration-500" />
      <h3 className="text-slate-200 font-semibold mb-1">Xu hướng theo tuần</h3>
      <p className="text-slate-500 text-xs mb-4">Số lượng vấn đề phân theo mức độ</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} barSize={12} barGap={4}>
          <defs>
            <linearGradient id="colorUrgent" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ef4444" stopOpacity={1}/>
              <stop offset="100%" stopColor="#ef4444" stopOpacity={0.4}/>
            </linearGradient>
            <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity={1}/>
              <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.4}/>
            </linearGradient>
            <linearGradient id="colorMedium" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={1}/>
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.4}/>
            </linearGradient>
            <linearGradient id="colorLow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity={1}/>
              <stop offset="100%" stopColor="#10b981" stopOpacity={0.4}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" vertical={false} />
          <XAxis
            dataKey="week"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            dy={10}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={25}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)', radius: 4 }} />
          <Bar dataKey="urgent" name="Khẩn cấp" fill="url(#colorUrgent)" radius={[4, 4, 0, 0]} />
          <Bar dataKey="high"   name="Cao"       fill="url(#colorHigh)" radius={[4, 4, 0, 0]} />
          <Bar dataKey="medium" name="Trung bình" fill="url(#colorMedium)" radius={[4, 4, 0, 0]} />
          <Bar dataKey="low"    name="Thấp"      fill="url(#colorLow)" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
