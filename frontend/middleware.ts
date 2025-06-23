import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  const supabase = createMiddlewareClient({ req, res });

  const {
    data: { session },
  } = await supabase.auth.getSession();

  const { pathname } = req.nextUrl;
  const targetHost = process.env.NEXT_PUBLIC_HOST || req.nextUrl.origin;

  // Define public paths
  const publicPaths = ['/', '/login'];
  const isAuthCallback = pathname.startsWith('/auth/callback'); // Supabase callback route
  const isPublicSupportRoute = pathname.startsWith('/dashboard/support');

  // If user has a session (logged in)
  if (session) {
    // If logged-in user tries to access /login, redirect to the homepage
    if (pathname === '/login') {
      return NextResponse.redirect(new URL('http://172.29.207.196/'));
    }
    // Allow access to all other routes for logged-in users
    return res;
  }

  // User does not have a session (not logged in)
  // Allow access to explicitly public paths, auth callback, and public support routes
  if (publicPaths.includes(pathname) || isAuthCallback || isPublicSupportRoute) {
    return res;
  }

  // For all other paths when not logged in, redirect to /login
  // This effectively protects all /dashboard/* routes except /dashboard/support/*
  return NextResponse.redirect(new URL('/login', targetHost));
}

export const config = {
  // Match all routes except for API routes, static files, image optimization files, favicon, and auth callback.
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|auth/callback).*)'],
}; 