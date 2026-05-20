import type { Metadata } from 'next';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';

export const metadata: Metadata = {
  title: 'Dashboard GVCN',
  description: 'Bảng điều khiển giáo viên chủ nhiệm — theo dõi vấn đề sinh viên theo thời gian thực.',
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-navy-950">
      {/* Sidebar cố định bên trái */}
      <Sidebar
        userName="ThS. Nguyễn Thị Lan"
        userEmail="lan.gvcn@hcmus.edu.vn"
        role="advisor"
        unreadCount={2}
      />
      {/* Nội dung chính */}
      <main className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        <Header />
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
