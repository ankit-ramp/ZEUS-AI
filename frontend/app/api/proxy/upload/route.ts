// zeus_frotned/app/api/proxy/upload/route.ts

import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

export async function POST(req: NextRequest) {
  try {
    const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;

    if (!backendBaseUrl) {
      console.error('SERVER ERROR: Environment variable NEXT_PUBLIC_BACKEND_BASE_URL is not set.');
      return new NextResponse('Backend URL configuration error.', { status: 500 });
    }

    const backendUploadUrl = `${backendBaseUrl}/upload`;

    // --- CRITICAL PART FOR MULTI-FILE FORWARDING ---
    // 1. Access the raw ReadableStream of the incoming request body
    const requestBodyStream = req.body; // This is a ReadableStream

    // 2. Prepare headers to be forwarded
    const forwardedHeaders = new Headers();
    // Copy all original headers that are safe to forward
    req.headers.forEach((value, key) => {
      // Exclude hop-by-hop headers that are specific to the current connection
      if (!['host', 'connection', 'content-length', 'transfer-encoding'].includes(key.toLowerCase())) {
        forwardedHeaders.set(key, value);
      }
    });

    // Ensure the Content-Type header (which contains the boundary) is explicitly set
    const contentType = req.headers.get('content-type');
    if (contentType) {
      forwardedHeaders.set('Content-Type', contentType);
    } else {
      console.warn('PROXY WARNING: Content-Type header missing from incoming request for upload.');
      // You might want to throw an error here if Content-Type is mandatory for your backend
    }

    // --- ENHANCED LOGGING ---
    console.log('PROXY: Received upload request to:', req.url);
    console.log('PROXY: Forwarding to backend:', backendUploadUrl);
    console.log('PROXY: Forwarding headers:', Object.fromEntries(forwardedHeaders.entries()));
    // You cannot easily log the raw stream content here without consuming it,
    // which would prevent it from being forwarded.

    const uploadResponse = await fetch(backendUploadUrl, {
      method: 'POST',
      // Pass the raw stream directly to the backend
      body: requestBodyStream,
      headers: forwardedHeaders,
      // @ts-ignore
      duplex: 'half' // Essential for piping streams with Node.js fetch
    });
    // --- END CRITICAL PART ---

    console.log('PROXY: Backend response status:', uploadResponse.status);

    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      console.error('PROXY ERROR: Backend upload failed.', {
        status: uploadResponse.status,
        response: errorText,
        headers: Object.fromEntries(uploadResponse.headers.entries()) // Log backend response headers
      });
      return new NextResponse(errorText, { status: uploadResponse.status });
    }

    const responseData = await uploadResponse.json();
    console.log('PROXY: Backend returned data (JSON):', responseData);

    return NextResponse.json(responseData, { status: uploadResponse.status });

  } catch (error) {
    console.error('PROXY GENERAL ERROR: An unexpected error occurred during upload proxy:', error);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}