import type { Metadata } from 'next';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'Dashboard GVCN — SSFT',
  description: 'Bảng điều khiển giáo viên chủ nhiệm — theo dõi vấn đề sinh viên theo thời gian thực.',
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar cố định bên trái */}
      <Sidebar
        userName="ThS. Nguyễn Thị Lan"
        userEmail="lan.gvcn@hcmus.edu.vn"
        role="advisor"
        unreadCount={2}
      />
      {/* Nội dung chính */}
      <main className="flex-1 min-w-0 overflow-auto">
        {children}
      </main>
    </div>
  );
}
