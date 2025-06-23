import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    const requestUrl = new URL(request.url);
    const code = requestUrl.searchParams.get('code');

    if (!code) {
      console.error('No code received in callback');
      return NextResponse.redirect(new URL('/login?error=no_code', request.url));
    }

    const supabase = createRouteHandlerClient({ cookies });
    const { data: { session }, error } = await supabase.auth.exchangeCodeForSession(code);
    
    if (error) {
      console.error('Auth error:', error);
      return NextResponse.redirect(new URL('/login?error=auth_failed', request.url));
    }

    if (!session) {
      console.error('No session created');
      return NextResponse.redirect(new URL('/login?error=no_session', request.url));
    }

    if (!session.user?.email) {
      console.error('No email in session');
      return NextResponse.redirect(new URL('/login?error=no_email', request.url));
    }

    // Successful login - redirect to dashboard
    return NextResponse.redirect(new URL('/dashboard', request.url));
  } catch (error) {
    console.error('Callback error:', error);
    return NextResponse.redirect(new URL('/login?error=callback_error', request.url));
  }
} 