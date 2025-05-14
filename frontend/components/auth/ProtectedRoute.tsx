import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../../lib/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If authentication is still loading, do nothing
    if (isLoading) return;
    
    // If the user is not authenticated, redirect to login
    if (!isAuthenticated) {
      router.push(`/auth/login?redirect=${encodeURIComponent(router.asPath)}`);
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Only render children if authenticated
  return isAuthenticated ? <>{children}</> : null;
} 