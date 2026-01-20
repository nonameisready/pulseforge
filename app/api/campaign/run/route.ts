import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const body = await req.json();
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL!;
  const r = await fetch(backend + '/campaign/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return NextResponse.json(await r.json());
}
