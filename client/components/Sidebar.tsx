'use client';

import { useRouter, usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LayoutDashboard, MessageSquare, GraduationCap,
  Bell, LogOut, ChevronRight, Users, BookOpen, Calendar
} from 'lucide-react';

interface SidebarProps {
  userName?: string;
  userEmail?: string;
  role?: 'advisor' | 'student';
  unreadCount?: number;
}

const advisorNav = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dashboard/chat', label: 'Trợ lý AI', icon: MessageSquare },
  { href: '/dashboard/students', label: 'Sinh viên', icon: Users },
  { href: '/dashboard/academic', label: 'Học vụ', icon: BookOpen },
  { href: '/dashboard/calendar', label: 'Lịch trình', icon: Calendar },
];

export function Sidebar({ userName, userEmail, role = 'advisor', unreadCount = 0 }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    sessionStorage.clear();
    router.push('/login');
  };

  const navItems = advisorNav;

  return (
    <motion.aside
      className="w-64 shrink-0 h-screen sticky top-0 flex flex-col
                 bg-navy-900/80 backdrop-blur-xl border-r border-white/[0.05]"
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* --- Logo --- */}
      <div className="px-6 py-5 border-b border-white/[0.05]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 to-blue-500
                          flex items-center justify-center shadow-glow-purple/30">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-sm tracking-wide">HTHT GVCN</p>
          </div>
        </div>
      </div>

      {/* --- Navigation --- */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <button
              key={item.href}
              onClick={() => router.push(item.href)}
              className={`nav-item w-full ${isActive ? 'active' : ''}`}
            >
              <item.icon className="w-4.5 h-4.5 w-[18px] h-[18px] shrink-0" />
              <span className="flex-1 text-left text-sm">{item.label}</span>
              {isActive && <ChevronRight className="w-3.5 h-3.5 opacity-50" />}
            </button>
          );
        })}
      </nav>

      {/* --- User Profile + Logout --- */}
      <div className="px-3 py-4 border-t border-white/[0.05] space-y-2">
        {/* Notification hint */}
        {unreadCount > 0 && (
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-purple-500/10 border border-purple-500/20">
            <Bell className="w-4 h-4 text-purple-400" />
            <span className="text-xs text-slate-300 flex-1">Thông báo chưa đọc</span>
            <span className="text-xs font-bold text-purple-300 bg-purple-500/20 px-2 py-0.5 rounded-full">
              {unreadCount}
            </span>
          </div>
        )}

        {/* User info */}
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500/40 to-blue-500/40
                          border border-purple-500/20 flex items-center justify-center shrink-0">
            <span className="text-xs font-bold text-purple-300">
              {(userName ?? userEmail ?? 'U')[0].toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-slate-200 text-xs font-medium truncate">
              {userName || 'GVCN'}
            </p>
            <p className="text-slate-500 text-xs truncate">{userEmail}</p>
          </div>
        </div>

      </div>
    </motion.aside>
  );
}
