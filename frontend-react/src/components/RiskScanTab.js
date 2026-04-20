import React, { useState, useRef } from 'react';

const API = 'http://localhost:8000';

// API scan response shape from main.py /scan:
// { session_id, overall_risk, overall_emoji, summary: { total_clauses, high_risk, medium_risk, low_risk },
//   high_risk_clauses, medium_risk_clauses, low_risk_clauses }
// Each clause: { clause_number, page, text, full_text, risk_level, risk_emoji }

const RISK = {
  HIGH:   { color: 'var(--red)',   bg: 'var(--red-bg)',   border: 'rgba(185,28,28,0.18)',   label: 'High Risk' },
  MEDIUM: { color: 'var(--amber)', bg: 'var(--amber-bg)', border: 'rgba(146,64,14,0.18)',   label: 'Medium Risk' },
  LOW:    { color: 'var(--green)', bg: 'var(--green-bg)', border: 'rgba(22,101,52,0.18)',   label: 'Low Risk' },
};

function ClauseCard({ clause }) {
  const [open, setOpen] = useState(false);
  const r = RISK[clause.risk_level] || RISK.LOW;
  return (
    <div className="fade-in" style={{
      border: `1px solid ${r.border}`,
      borderLeft: `3px solid ${r.color}`,
      borderRadius: 8, marginBottom: 8, overflow: 'hidden',
      background: 'var(--surface)',
    }}>
      {/* Header row */}
      <div onClick={() => setOpen(o => !o)} style={{
        display: 'flex', alignItems: 'center', gap: 9,
        padding: '10px 12px', cursor: 'pointer',
      }}>
        <span style={{ fontSize: '0.7rem', color: 'var(--text3)', fontFamily: 'var(--font-mono)', flexShrink: 0 }}>
          #{clause.clause_number}
        </span>
        <span style={{
          background: r.bg, color: r.color,
          fontSize: '0.63rem', fontWeight: 700,
          padding: '2px 8px', borderRadius: 4, flexShrink: 0,
          letterSpacing: '0.04em',
        }}>{r.label}</span>
        <span style={{
          flex: 1, fontSize: '0.8rem', color: 'var(--text2)',
          overflow: 'hidden', textOverflow: 'ellipsis',
          whiteSpace: open ? 'normal' : 'nowrap',
        }}>
          {/* Show truncated text from API (already trimmed to 300 chars) */}
          {clause.text}
        </span>
        <span style={{ color: 'var(--text3)', fontSize: '0.75rem', flexShrink: 0 }}>
          {open ? '▲' : '▼'}
        </span>
      </div>

      {/* Expanded body — show full_text */}
      {open && (
        <div style={{
          borderTop: '1px solid var(--border)', padding: '11px 12px',
          background: 'var(--bg)',
        }}>
          {clause.page !== '?' && (
            <div style={{ fontSize: '0.67rem', color: 'var(--text3)', marginBottom: 6 }}>
              Page {clause.page}
            </div>
          )}
          <div style={{
            fontSize: '0.8rem', color: 'var(--text2)', lineHeight: 1.65,
            whiteSpace: 'pre-wrap', fontFamily: 'var(--font-mono)',
          }}>
            {clause.full_text || clause.text}
          </div>
        </div>
      )}
    </div>
  );
}

function ClauseSection({ title, clauses, riskKey }) {
  if (!clauses || clauses.length === 0) return null;
  const r = RISK[riskKey];
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{
        fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.1em',
        textTransform: 'uppercase', color: r.color, marginBottom: 8,
      }}>
        {title} ({clauses.length})
      </div>
      {clauses.map((c, i) => <ClauseCard key={i} clause={c} />)}
    </div>
  );
}

export default function RiskScanTab({ session, setSession }) {
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState(null);  // full scan response
  const [error, setError] = useState('');
  const fileRef = useRef();

  const runScan = async () => {
    setScanning(true); setError(''); setResults(null);
    let sid = session?.id;

    // If no session but file selected, upload first
    if (!sid && file) {
      const fd = new FormData();
      fd.append('file', file);
      try {
        const res = await fetch(`${API}/upload`, { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) { setError(data.detail || 'Upload failed'); setScanning(false); return; }
        sid = data.session_id;
        setSession({ id: sid, filename: data.filename, chunks: data.chunks, pages: data.pages });
      } catch {
        setError('API offline — run: python api/main.py');
        setScanning(false); return;
      }
    }

    if (!sid) { setError('Upload a contract first.'); setScanning(false); return; }

    try {
      // POST /scan with { session_id }
      const res = await fetch(`${API}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sid }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Scan failed'); setScanning(false); return; }
      // data = { session_id, overall_risk, overall_emoji, summary, high_risk_clauses, medium_risk_clauses, low_risk_clauses }
      setResults(data);
      setFile(null);
    } catch {
      setError('API offline — run: python api/main.py');
    }
    setScanning(false);
  };

  const reset = () => { setResults(null); setError(''); };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

      {/* Header */}
      <div style={{ padding: '16px 26px 12px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
        <div style={{ fontFamily: 'var(--font-serif)', fontSize: '1.4rem', fontWeight: 600, color: 'var(--text)' }}>
          Risk Scanner
        </div>
        <div style={{ fontSize: '0.73rem', color: 'var(--text3)', marginTop: 2 }}>
          Clause-by-clause analysis cross-referenced against Indian contract law
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '22px 26px' }}>

        {/* ── Upload / scan controls ── */}
        {!results && (
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 12, padding: 22, maxWidth: 540,
          }}>

            {/* Already have session */}
            {session ? (
              <div style={{
                display: 'flex', gap: 10, alignItems: 'center',
                background: 'var(--green-bg)', border: '1px solid rgba(22,101,52,0.18)',
                borderRadius: 8, padding: '10px 14px', marginBottom: 14,
              }}>
                <span>📄</span>
                <div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text)', fontWeight: 600 }}>{session.filename}</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text3)' }}>{session.pages} pages · {session.chunks} chunks · ready</div>
                </div>
              </div>
            ) : (
              /* Upload zone */
              <div style={{ marginBottom: 14 }}>
                <div onClick={() => fileRef.current?.click()} style={{
                  border: '1.5px dashed var(--border2)', borderRadius: 10,
                  padding: '28px 18px', textAlign: 'center', cursor: 'pointer',
                  background: file ? 'var(--brown-glow)' : 'var(--bg)',
                  transition: 'background 0.15s',
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: 6 }}>☁</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text2)', fontWeight: 500 }}>
                    {file ? file.name : 'Upload a contract PDF'}
                  </div>
                  <div style={{ fontSize: '0.73rem', color: 'var(--text3)', marginTop: 3 }}>
                    {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Click to browse'}
                  </div>
                </div>
                <input ref={fileRef} type="file" accept=".pdf" style={{ display: 'none' }}
                  onChange={e => { setFile(e.target.files[0]); setError(''); }} />
              </div>
            )}

            <button
              onClick={runScan}
              disabled={(!session && !file) || scanning}
              style={{
                width: '100%', padding: 11, borderRadius: 8,
                border: 'none',
                background: (session || file) && !scanning ? 'var(--brown)' : 'var(--bg2)',
                color: (session || file) && !scanning ? '#fff' : 'var(--text3)',
                fontSize: '0.875rem', fontWeight: 600,
                transition: 'background 0.15s',
              }}>
              {scanning ? '⟳  Scanning clauses…' : 'Run Risk Scan'}
            </button>

            {error && (
              <div style={{
                marginTop: 10, background: 'var(--red-bg)',
                border: '1px solid rgba(185,28,28,0.18)',
                borderRadius: 8, padding: '9px 12px',
                fontSize: '0.78rem', color: 'var(--red)',
              }}>{error}</div>
            )}

            {/* What it looks for */}
            <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.65rem', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.09em', marginBottom: 8 }}>
                What it scans for
              </div>
              {[
                ['HIGH',   'Termination, liability caps, penalties, indemnity'],
                ['MEDIUM', 'Payment terms, IP ownership, exclusivity, warranties'],
                ['LOW',    'Standard boilerplate, definitions, notices'],
              ].map(([level, desc]) => (
                <div key={level} style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'flex-start' }}>
                  <span style={{
                    background: RISK[level].bg, color: RISK[level].color,
                    fontSize: '0.62rem', fontWeight: 700,
                    padding: '1px 7px', borderRadius: 3, flexShrink: 0, marginTop: 1,
                  }}>{level}</span>
                  <span style={{ fontSize: '0.77rem', color: 'var(--text2)' }}>{desc}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Results ── */}
        {results && (
          <div className="fade-in">

            {/* Summary bar */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
              {/* Overall risk */}
              <div style={{
                flex: 1.2, padding: '14px 16px', borderRadius: 10,
                background: RISK[results.overall_risk]?.bg || 'var(--bg2)',
                border: `1px solid ${RISK[results.overall_risk]?.border || 'var(--border)'}`,
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '1.4rem' }}>{results.overall_emoji}</div>
                <div style={{ fontSize: '0.7rem', color: RISK[results.overall_risk]?.color || 'var(--text2)', fontWeight: 700, marginTop: 2 }}>
                  {results.overall_risk} RISK
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text3)', marginTop: 1 }}>overall</div>
              </div>

              {/* Count cards — from summary object */}
              {[
                ['HIGH',   results.summary.high_risk],
                ['MEDIUM', results.summary.medium_risk],
                ['LOW',    results.summary.low_risk],
              ].map(([level, count]) => (
                <div key={level} style={{
                  flex: 1, padding: '12px 14px', borderRadius: 10, textAlign: 'center',
                  background: RISK[level].bg, border: `1px solid ${RISK[level].border}`,
                }}>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700, color: RISK[level].color, fontFamily: 'var(--font-mono)' }}>
                    {count}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: RISK[level].color, opacity: 0.85, marginTop: 2 }}>
                    {RISK[level].label}
                  </div>
                </div>
              ))}

              <div style={{
                flex: 1, padding: '12px 14px', borderRadius: 10, textAlign: 'center',
                background: 'var(--surface)', border: '1px solid var(--border)',
              }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text)', fontFamily: 'var(--font-mono)' }}>
                  {results.summary.total_clauses}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text3)', marginTop: 2 }}>Total</div>
              </div>
            </div>

            {/* Action row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <div style={{ fontFamily: 'var(--font-serif)', fontSize: '1.1rem', color: 'var(--text)', fontWeight: 600 }}>
                Clause Analysis
              </div>
              <button onClick={reset} style={{
                background: 'transparent', border: '1px solid var(--border)',
                borderRadius: 6, padding: '5px 12px',
                fontSize: '0.74rem', color: 'var(--text3)',
              }}>← New Scan</button>
            </div>

            {/* Clause lists — using the three separate arrays from API */}
            <ClauseSection title="High Risk" clauses={results.high_risk_clauses}   riskKey="HIGH" />
            <ClauseSection title="Medium Risk" clauses={results.medium_risk_clauses} riskKey="MEDIUM" />
            <ClauseSection title="Low Risk"  clauses={results.low_risk_clauses}    riskKey="LOW" />
          </div>
        )}
      </div>
    </div>
  );
}