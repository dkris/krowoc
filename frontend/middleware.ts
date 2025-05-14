import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { createServerClient, type CookieOptions } from '@supabase/ssr';

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value;
        },
        set(name: string, value: string, options: CookieOptions) {
          response.cookies.set({
            name,
            value,
            ...options,
          });
        },
        remove(name: string, options: CookieOptions) {
          response.cookies.set({
            name,
            value: '',
            ...options,
          });
        },
      },
    }
  );

  // Refresh the session if it exists
  const { data: { session } } = await supabase.auth.getSession();

  // Protected routes logic
  const protectedRoutes = ['/profile'];
  const isProtectedRoute = protectedRoutes.some(route => 
    request.nextUrl.pathname.startsWith(route)
  );

  if (isProtectedRoute && !session) {
    // Redirect to login if accessing a protected route without a session
    const redirectUrl = new URL('/auth/login', request.url);
    redirectUrl.searchParams.set('redirect', request.nextUrl.pathname);
    return NextResponse.redirect(redirectUrl);
  }

  // Auth route logic - redirect to home if already logged in
  const authRoutes = ['/auth/login', '/auth/signup', '/auth/reset-password'];
  const isAuthRoute = authRoutes.some(route => 
    request.nextUrl.pathname.startsWith(route)
  );

  if (isAuthRoute && session) {
    // If the user is already logged in and trying to access an auth page, redirect to home
    return NextResponse.redirect(new URL('/', request.url));
  }

  return response;
}

export const config = {
  matcher: [
    // Match all request paths except for static files, api routes, etc.
    '/((?!_next/static|_next/image|favicon.ico|api).*)',
  ],
}; 