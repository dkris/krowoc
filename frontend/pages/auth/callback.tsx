import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { supabase } from '../../lib/supabase';

export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Exchange the code for a session
        const { data, error } = await supabase.auth.exchangeCodeForSession(
          window.location.search.substring(1)
        );
        
        if (error) {
          throw error;
        }
        
        // Redirect to home page on success
        router.push('/');
      } catch (error) {
        console.error('Error during OAuth callback:', error);
        router.push('/auth/login?error=oauth_callback_failed');
      }
    };
    
    // Don't try to handle the callback until the router is ready
    if (router.isReady) {
      handleAuthCallback();
    }
  }, [router]);
  
  return (
    <div className="flex justify-center items-center min-h-[50vh]">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
      <p className="ml-3 text-sm text-gray-700">Completing authentication...</p>
    </div>
  );
} 