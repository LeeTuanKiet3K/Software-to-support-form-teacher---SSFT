import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Hệ thống Hỗ trợ Giáo viên chủ nhiệm',
  description: 'Phần mềm AI hỗ trợ Giáo viên chủ nhiệm quản lý, tư vấn và phân loại vấn đề sinh viên tự động.',
  keywords: ['GVCN', 'sinh viên', 'AI', 'tư vấn học tập'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className="dark">
      <body className="animated-bg min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
