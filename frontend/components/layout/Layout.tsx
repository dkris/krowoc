import { ReactNode } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuth } from '../../lib/AuthContext';
import { signOut } from '../../lib/supabase';

type LayoutProps = {
  children: ReactNode;
  title?: string;
};

export default function Layout({ children, title = 'Krowoc' }: LayoutProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  
  const handleSignOut = async () => {
    await signOut();
    router.push('/');
  };
  
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="Krowoc application" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="flex min-h-screen flex-col">
        <header className="bg-white shadow">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-8">
                <Link href="/" className="flex items-center">
                  <h1 className="text-2xl font-bold tracking-tight text-gray-900">{title}</h1>
                </Link>
                
                {!isLoading && user && (
                  <nav className="flex items-center space-x-6">
                    <Link 
                      href="/prompts" 
                      className={`text-sm font-medium ${
                        router.pathname.startsWith('/prompts') 
                          ? 'text-blue-600' 
                          : 'text-gray-500 hover:text-gray-900'
                      }`}
                    >
                      Prompts
                    </Link>
                    <Link 
                      href="/dashboard" 
                      className={`text-sm font-medium ${
                        router.pathname === '/dashboard' 
                          ? 'text-blue-600' 
                          : 'text-gray-500 hover:text-gray-900'
                      }`}
                    >
                      Dashboard
                    </Link>
                    <Link 
                      href="/profile" 
                      className={`text-sm font-medium ${
                        router.pathname === '/profile' 
                          ? 'text-blue-600' 
                          : 'text-gray-500 hover:text-gray-900'
                      }`}
                    >
                      Profile
                    </Link>
                    <Link 
                      href="/settings" 
                      className={`text-sm font-medium ${
                        router.pathname === '/settings' 
                          ? 'text-blue-600' 
                          : 'text-gray-500 hover:text-gray-900'
                      }`}
                    >
                      Settings
                    </Link>
                  </nav>
                )}
              </div>
              
              <div className="flex items-center">
                {!isLoading && (
                  user ? (
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-700">
                        {user.email}
                      </span>
                      <button
                        onClick={handleSignOut}
                        className="text-sm font-medium text-blue-600 hover:text-blue-500"
                      >
                        Sign out
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-4">
                      <Link href="/auth/login" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                        Sign in
                      </Link>
                      <Link 
                        href="/auth/signup"
                        className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
                      >
                        Sign up
                      </Link>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        </header>
        <main className="flex-grow">
          <div className="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
        <footer className="bg-white">
          <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-gray-500">
              © {new Date().getFullYear()} Krowoc. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
} 