// zeus_frotned/app/api/proxy/download/route.ts

import { NextRequest, NextResponse } from 'next/server';

// --- ADD THESE LINES ---
export const dynamic = 'force-dynamic';     // Ensures the route is always executed dynamically
export const fetchCache = 'force-no-store'; // Prevents Next.js's own fetch caching behavior
// --- END ADDITIONS ---

export async function GET(req: NextRequest) {
  try {
    const backendDownloadUrl = `${process.env.NEXT_PUBLIC_BACKEND_BASE_URL}/download`; // Your actual backend download endpoint

    const downloadResponse = await fetch(backendDownloadUrl);
    console.log('Download response:', downloadResponse);

    if (!downloadResponse.ok) {
      const errorText = await downloadResponse.text();
      return new NextResponse(errorText, { status: downloadResponse.status });
    }

    // Forward the content-type and other headers from the backend response
    const headers = new Headers(downloadResponse.headers);
    // You might want to explicitly set Content-Disposition if it's not coming from backend
    // headers.set('Content-Disposition', 'attachment; filename="results.xlsx"');

    return new NextResponse(downloadResponse.body, { status: downloadResponse.status, headers });

  } catch (error) {
    console.error('Proxy download error:', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}