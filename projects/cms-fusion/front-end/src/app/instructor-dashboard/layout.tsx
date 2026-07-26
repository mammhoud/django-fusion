import AuthGuard from '@/components/AuthGuard';

export default function InstructorDashboardLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>;
}
