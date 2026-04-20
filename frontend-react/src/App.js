import React, { useState } from 'react';
import './index.css';
import ChatTab from './components/ChatTab';
import RiskScanTab from './components/RiskScanTab';
import EvalTab from './components/EvalTab';

const NAV = [
  { id: 'chat', label: 'Ask LexIQ' },
  { id: 'scan', label: 'Risk Scanner' },
  { id: 'eval', label: 'Eval Results' },
];

const SAMPLE_QUESTIONS = [
  'Penalty for breach of contract?',
  'MSME 45-day payment rule?',
  'GST invoice requirements?',
  'What voids a contract in India?',
  'Explain force majeure clause',
];

export default function App() {
  const [tab, setTab] = useState('chat');
  const [session, setSession] = useState(null); // { id, filename, pages, chunks }
  const [pendingQ, setPendingQ] = useState(null);

  const fireQuestion = (q) => {
    setTab('chat');
    setPendingQ(q);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: 'var(--bg)' }}>

      {/* Sidebar */}
      <aside style={{
        width: 'var(--sidebar-w)', minWidth: 'var(--sidebar-w)',
        background: 'var(--surface)',
        borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column',
        height: '100vh', position: 'fixed', top: 0, left: 0, zIndex: 10,
      }}>
        {/* Logo */}
        <div style={{ padding: '26px 22px 18px', borderBottom: '1px solid var(--border)' }}>
          <div style={{
            fontFamily: 'var(--font-serif)', fontSize: '1.75rem', fontWeight: 600,
            color: 'var(--brown)', letterSpacing: '0.01em', lineHeight: 1,
          }}>LexIQ</div>
          <div style={{
            fontSize: '0.68rem', color: 'var(--text3)', marginTop: 4,
            letterSpacing: '0.1em', textTransform: 'uppercase',
          }}>Legal Intelligence</div>
        </div>

        {/* Nav links */}
        <nav style={{ padding: '8px 0', flex: 1 }}>
          <div style={{
            padding: '8px 18px 6px', fontSize: '0.63rem', color: 'var(--text3)',
            letterSpacing: '0.12em', textTransform: 'uppercase',
          }}>Navigation</div>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setTab(n.id)} style={{
              display: 'block', width: '100%', textAlign: 'left',
              padding: '9px 18px', border: 'none',
              borderLeft: `3px solid ${tab === n.id ? 'var(--brown)' : 'transparent'}`,
              background: tab === n.id ? 'var(--brown-dim)' : 'transparent',
              color: tab === n.id ? 'var(--brown)' : 'var(--text2)',
              fontSize: '0.85rem', fontWeight: tab === n.id ? 600 : 400,
              transition: 'all 0.12s',
            }}>{n.label}</button>
          ))}
        </nav>

        {/* Sample questions */}
        <div style={{ padding: '12px 18px', borderTop: '1px solid var(--border)' }}>
          <div style={{
            fontSize: '0.63rem', color: 'var(--text3)',
            letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 8,
          }}>Try These</div>
          {SAMPLE_QUESTIONS.map(q => (
            <button key={q} onClick={() => fireQuestion(q)} style={{
              display: 'block', width: '100%', textAlign: 'left',
              background: 'transparent', border: 'none',
              color: 'var(--text3)', fontSize: '0.74rem',
              padding: '4px 0', lineHeight: 1.45, cursor: 'pointer',
              transition: 'color 0.12s',
            }}
              onMouseEnter={e => e.currentTarget.style.color = 'var(--brown)'}
              onMouseLeave={e => e.currentTarget.style.color = 'var(--text3)'}
            >→ {q}</button>
          ))}
        </div>

        {/* Session status */}
        <div style={{
          padding: '10px 18px', borderTop: '1px solid var(--border)',
          fontSize: '0.7rem', color: 'var(--text3)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{
              width: 7, height: 7, borderRadius: '50%', display: 'inline-block',
              background: session ? 'var(--green)' : 'var(--text3)',
            }} />
            {session ? `Session active` : 'No contract loaded'}
          </div>
          {session?.filename && (
            <div style={{
              marginTop: 2, color: 'var(--text2)', fontSize: '0.68rem',
              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
            }}>{session.filename}</div>
          )}
        </div>
      </aside>

      {/* Main */}
      <main style={{ marginLeft: 'var(--sidebar-w)', flex: 1, height: '100vh', overflow: 'hidden' }}>
        {tab === 'chat' && <ChatTab session={session} setSession={setSession} pendingQ={pendingQ} setPendingQ={setPendingQ} />}
        {tab === 'scan' && <RiskScanTab session={session} setSession={setSession} />}
        {tab === 'eval' && <EvalTab />}
      </main>
    </div>
  );
}