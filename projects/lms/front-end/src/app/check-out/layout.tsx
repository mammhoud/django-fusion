import AuthGuard from '@/components/AuthGuard';

export default function CheckoutLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>;
}
