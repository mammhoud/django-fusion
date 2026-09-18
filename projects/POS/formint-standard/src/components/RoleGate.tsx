import type { ReactNode } from 'react';
import { usePermissions, type PermissionKey } from '../hooks/usePermissions';

interface RoleGateProps {
  permission: PermissionKey;
  children: ReactNode;
  fallback?: ReactNode;
}

/** Render children only when the current user holds the requested permission. */
export default function RoleGate({ permission, children, fallback = null }: RoleGateProps) {
  const { can, isLoading } = usePermissions();
  if (isLoading) return null;
  return can(permission) ? <>{children}</> : <>{fallback}</>;
}
