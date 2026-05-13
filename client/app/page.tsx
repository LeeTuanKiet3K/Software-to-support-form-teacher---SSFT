import { redirect } from 'next/navigation';

// Trang gốc - tự động chuyển về /login
export default function HomePage() {
  redirect('/login');
}
