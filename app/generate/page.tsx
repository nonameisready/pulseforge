'use client';
import { useState } from 'react';

export default function Generate() {
  const [out, setOut] = useState<any>(null);

  async function run() {
    const res = await fetch('/api/campaign/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_name: "Whispered Atelier — Couture Evening Gown",
        product_desc: "High-end couture evening gown, premium fabrics",
        num_variants: 12
      })
    });
    setOut(await res.json());
  }

  return (
    <main style={{padding:40}}>
      <h2>Generate Ads</h2>
      <button onClick={run}>Run Agent</button>
      <pre>{out && JSON.stringify(out, null, 2)}</pre>
    </main>
  );
}
