import AuthGuard from '@/components/AuthGuard';

export default function CartLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>;
}
