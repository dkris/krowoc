import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import AuthForm from '../../components/auth/AuthForm';
import { useAuth } from '../../lib/AuthContext';

export default function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  
  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      router.push('/');
    }
  }, [isAuthenticated, isLoading, router]);
  
  const handleSuccess = () => {
    router.push('/');
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (isAuthenticated) {
    return null; // Will redirect via useEffect
  }
  
  return (
    <div className="py-8">
      <AuthForm type="login" onSuccess={handleSuccess} />
      
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Don't have an account?{' '}
          <Link href="/auth/signup" className="font-medium text-blue-600 hover:text-blue-500">
            Sign up
          </Link>
        </p>
        <p className="mt-2 text-sm text-gray-600">
          <Link href="/auth/reset-password" className="font-medium text-blue-600 hover:text-blue-500">
            Forgot your password?
          </Link>
        </p>
      </div>
    </div>
  );
} 