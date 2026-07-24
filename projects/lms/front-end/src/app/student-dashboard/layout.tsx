import AuthGuard from '@/components/AuthGuard';

export default function StudentDashboardLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>;
}
