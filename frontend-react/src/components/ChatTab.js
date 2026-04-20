import React, { useState, useRef, useEffect } from 'react';

const API = 'http://localhost:8000';

// Risk badge using exact values from risk_scorer.py: HIGH / MEDIUM / LOW
function RiskBadge({ level }) {
  const cfg = {
    HIGH:    { bg: 'var(--red-bg)',   color: 'var(--red)',   label: 'High Risk' },
    MEDIUM:  { bg: 'var(--amber-bg)', color: 'var(--amber)', label: 'Medium Risk' },
    LOW:     { bg: 'var(--green-bg)', color: 'var(--green)', label: 'Low Risk' },
    UNKNOWN: { bg: 'var(--bg2)',      color: 'var(--text3)', label: 'Unknown' },
  };
  const s = cfg[level] || cfg.UNKNOWN;
  return (
    <span style={{
      background: s.bg, color: s.color,
      fontSize: '0.7rem', fontWeight: 600,
      padding: '2px 9px', borderRadius: 4,
      border: `1px solid ${s.color}22`,
    }}>{s.label}</span>
  );
}

// Each source from sources[] array:  { filename, page, category, risk_level, risk_emoji }
function SourceChip({ src }) {
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      background: 'var(--bg2)', border: '1px solid var(--border)',
      borderRadius: 5, padding: '3px 9px', fontSize: '0.68rem',
      color: 'var(--text2)', fontFamily: 'var(--font-mono)',
    }}>
      <span>{src.risk_emoji}</span>
      <span>{src.filename}</span>
      {src.page !== '?' && <span style={{ color: 'var(--text3)' }}>p.{src.page}</span>}
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className="fade-in" style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 18, gap: 10, alignItems: 'flex-start',
    }}>
      {!isUser && (
        <div style={{
          width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
          background: 'var(--brown-dim)', border: '1.5px solid var(--brown)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.78rem', color: 'var(--brown)', fontWeight: 700,
          fontFamily: 'var(--font-serif)', marginTop: 2,
        }}>L</div>
      )}

      <div style={{ maxWidth: '72%' }}>
        {/* Message bubble */}
        <div style={{
          background: isUser ? 'var(--brown-dim)' : 'var(--surface)',
          border: `1px solid ${isUser ? 'var(--border2)' : 'var(--border)'}`,
          borderRadius: isUser ? '14px 14px 2px 14px' : '2px 14px 14px 14px',
          padding: '11px 15px',
          color: 'var(--text)', fontSize: '0.875rem', lineHeight: 1.7,
          whiteSpace: 'pre-wrap',
        }}>{msg.content}</div>

        {/* Sources — from sources[] in QueryResponse */}
        {msg.sources && msg.sources.length > 0 && (
          <div style={{ marginTop: 7, display: 'flex', flexWrap: 'wrap', gap: 5 }}>
            {msg.sources.map((s, i) => <SourceChip key={i} src={s} />)}
          </div>
        )}

        {/* Risk level — from risk_level in QueryResponse */}
        {msg.risk_level && msg.risk_level !== 'UNKNOWN' && (
          <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center' }}>
            <RiskBadge level={msg.risk_level} />
            <span style={{ fontSize: '0.68rem', color: 'var(--text3)' }}>RAG · {msg.sources?.length || 0} sources</span>
          </div>
        )}

        {/* No-RAG comparison toggle */}
        {msg.no_rag_answer && <NoRagToggle noRag={msg.no_rag_answer} />}
      </div>

      {isUser && (
        <div style={{
          width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
          background: 'var(--bg2)', border: '1px solid var(--border2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.62rem', color: 'var(--text2)', fontWeight: 600,
          marginTop: 2,
        }}>You</div>
      )}
    </div>
  );
}

function NoRagToggle({ noRag }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ marginTop: 6 }}>
      <button onClick={() => setOpen(o => !o)} style={{
        background: 'transparent', border: 'none',
        fontSize: '0.68rem', color: 'var(--text3)', cursor: 'pointer',
        padding: 0, textDecoration: 'underline',
      }}>
        {open ? '▲ Hide' : '▼ Show'} baseline (no RAG)
      </button>
      {open && (
        <div style={{
          marginTop: 5, padding: '9px 12px',
          background: 'var(--bg2)', border: '1px solid var(--border)',
          borderRadius: 8, fontSize: '0.78rem', color: 'var(--text2)',
          lineHeight: 1.6, whiteSpace: 'pre-wrap',
        }}>{noRag}</div>
      )}
    </div>
  );
}

function UploadPanel({ session, setSession }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileRef = useRef();

  const upload = async () => {
    if (!file) return;
    setLoading(true); setError('');
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await fetch(`${API}/upload`, { method: 'POST', body: fd });
      const data = await res.json();
      if (!res.ok) { setError(data.detail || 'Upload failed'); setLoading(false); return; }
      // data = { session_id, filename, chunks, pages, message }
      setSession({ id: data.session_id, filename: data.filename, chunks: data.chunks, pages: data.pages });
      setFile(null);
    } catch {
      setError('API offline — run: python api/main.py');
    }
    setLoading(false);
  };

  const clear = async () => {
    if (session?.id) {
      try { await fetch(`${API}/session/${session.id}`, { method: 'DELETE' }); } catch {}
    }
    setSession(null);
  };

  return (
    <div style={{
      background: 'var(--surface)', border: '1px solid var(--border)',
      borderRadius: 10, padding: 14, marginBottom: 12,
    }}>
      <div style={{ fontSize: '0.65rem', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>
        Contract
      </div>

      {session ? (
        <>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 10 }}>
            <span>📄</span>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text)', fontWeight: 600 }}>{session.filename}</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text3)' }}>{session.pages} pages · {session.chunks} chunks</div>
            </div>
          </div>
          <button onClick={clear} style={{
            width: '100%', padding: '7px', borderRadius: 6,
            background: 'var(--red-bg)', border: '1px solid rgba(185,28,28,0.2)',
            color: 'var(--red)', fontSize: '0.78rem', fontWeight: 500,
          }}>Clear Contract</button>
        </>
      ) : (
        <>
          <div onClick={() => fileRef.current?.click()} style={{
            border: '1.5px dashed var(--border2)', borderRadius: 8,
            padding: '18px 10px', textAlign: 'center', cursor: 'pointer',
            background: file ? 'var(--brown-glow)' : 'var(--bg)',
            marginBottom: 8,
          }}>
            <div style={{ fontSize: '1.3rem', marginBottom: 4 }}>☁</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text2)', fontWeight: 500 }}>
              {file ? file.name : 'Drop PDF or click'}
            </div>
            {file && <div style={{ fontSize: '0.68rem', color: 'var(--text3)', marginTop: 2 }}>
              {(file.size / 1024).toFixed(1)} KB
            </div>}
          </div>
          <input ref={fileRef} type="file" accept=".pdf" style={{ display: 'none' }}
            onChange={e => { setFile(e.target.files[0]); setError(''); }} />
          {file && (
            <button onClick={upload} disabled={loading} style={{
              width: '100%', padding: '8px', borderRadius: 6,
              background: loading ? 'var(--bg3)' : 'var(--brown)',
              border: 'none', color: '#fff',
              fontSize: '0.8rem', fontWeight: 600,
            }}>{loading ? 'Processing…' : '⚙ Process Contract'}</button>
          )}
          {error && <div style={{ marginTop: 7, fontSize: '0.74rem', color: 'var(--red)' }}>{error}</div>}
        </>
      )}
    </div>
  );
}

export default function ChatTab({ session, setSession, pendingQ, setPendingQ }) {
  const [messages, setMessages] = useState([{
    role: 'assistant',
    content: 'Welcome to LexIQ. I can answer questions about Indian contract law, GST compliance, MSME regulations, employment law, and more — drawing from 38 legal documents.\n\nUpload a contract on the right for clause-specific analysis.',
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();
  const textareaRef = useRef();

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  useEffect(() => {
    if (pendingQ) { send(pendingQ); setPendingQ(null); }
  }, [pendingQ]);

  const send = async (text) => {
    const q = (text || input).trim();
    if (!q || loading) return;
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setLoading(true);

    try {
      const res = await fetch(`${API}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // POST body matches QueryRequest: { question, session_id, strategy, top_k }
        body: JSON.stringify({
          question: q,
          session_id: session?.id || null,
          strategy: 'clause',
          top_k: 5,
        }),
      });
      const data = await res.json();

      if (!res.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${data.detail || 'Query failed.'}` }]);
      } else {
        // Map QueryResponse fields: answer, sources, risk_level, risk_emoji, no_rag_answer
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
          risk_level: data.risk_level,
          risk_emoji: data.risk_emoji,
          no_rag_answer: data.no_rag_answer,
        }]);
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠ Cannot reach API. Make sure to run: python api/main.py',
      }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>

      {/* Chat column */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {/* Header */}
        <div style={{ padding: '16px 26px 12px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
          <div style={{ fontFamily: 'var(--font-serif)', fontSize: '1.4rem', fontWeight: 600, color: 'var(--text)' }}>
            Ask LexIQ
          </div>
          <div style={{ fontSize: '0.73rem', color: 'var(--text3)', marginTop: 2 }}>
            Groq · llama-3.1-8b-instant · 38 Indian legal documents
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '22px 26px' }}>
          {messages.map((m, i) => <Message key={i} msg={m} />)}
          {loading && (
            <div className="fade-in" style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 18 }}>
              <div style={{
                width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                background: 'var(--brown-dim)', border: '1.5px solid var(--brown)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.78rem', color: 'var(--brown)', fontFamily: 'var(--font-serif)', fontWeight: 700,
              }}>L</div>
              <div style={{
                background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: '2px 14px 14px 14px', padding: '13px 16px',
              }}>
                <div style={{ display: 'flex', gap: 5 }}>
                  {[0, 0.18, 0.36].map(d => (
                    <div key={d} className="pulse" style={{
                      width: 7, height: 7, borderRadius: '50%',
                      background: 'var(--brown)', animationDelay: `${d}s`,
                    }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <div style={{
          padding: '12px 26px 18px',
          borderTop: '1px solid var(--border)',
          background: 'var(--bg)', flexShrink: 0,
        }}>
          <div style={{
            display: 'flex', gap: 8, alignItems: 'flex-end',
            background: 'var(--surface)', border: '1.5px solid var(--border2)',
            borderRadius: 12, padding: '4px 4px 4px 14px',
          }}>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
              placeholder="Ask about Indian contract law, GST, MSME…"
              rows={1}
              style={{
                flex: 1, background: 'transparent', border: 'none', outline: 'none',
                color: 'var(--text)', fontSize: '0.875rem', resize: 'none',
                padding: '9px 0', lineHeight: 1.5, maxHeight: 120,
                fontFamily: 'var(--font-sans)',
              }}
              onInput={e => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />
            <button
              onClick={() => send()}
              disabled={!input.trim() || loading}
              style={{
                width: 36, height: 36, borderRadius: 8, flexShrink: 0,
                background: input.trim() && !loading ? 'var(--brown)' : 'var(--bg2)',
                border: 'none',
                color: input.trim() && !loading ? '#fff' : 'var(--text3)',
                fontSize: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'background 0.15s',
              }}>↑</button>
          </div>
          <div style={{ fontSize: '0.66rem', color: 'var(--text3)', marginTop: 5, textAlign: 'center' }}>
            Enter to send · Shift+Enter for new line
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div style={{
        width: 272, flexShrink: 0, borderLeft: '1px solid var(--border)',
        padding: 14, overflowY: 'auto', background: 'var(--bg)',
      }}>
        <UploadPanel session={session} setSession={setSession} />

        {/* Last response info */}
        {messages.filter(m => m.role === 'assistant' && m.risk_level).length > 0 && (() => {
          const last = messages.filter(m => m.role === 'assistant' && m.risk_level).slice(-1)[0];
          return (
            <div style={{
              background: 'var(--surface)', border: '1px solid var(--border)',
              borderRadius: 10, padding: 12, marginBottom: 12,
            }}>
              <div style={{ fontSize: '0.65rem', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>
                Last Response
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <span style={{ fontSize: '0.73rem', color: 'var(--text2)' }}>Risk:</span>
                <RiskBadge level={last.risk_level} />
              </div>
              {last.sources?.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text3)', marginBottom: 4 }}>Sources used:</div>
                  {last.sources.slice(0, 4).map((s, i) => (
                    <div key={i} style={{ fontSize: '0.69rem', color: 'var(--text2)', fontFamily: 'var(--font-mono)', padding: '2px 0' }}>
                      {s.risk_emoji} {s.filename}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })()}

        {/* Knowledge base */}
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 10, padding: 12,
        }}>
          <div style={{ fontSize: '0.65rem', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>
            Knowledge Base
          </div>
          {[
            ['Legislation', '20 acts'],
            ['GST & Compliance', '8 docs'],
            ['MSME Rules', '3 docs'],
            ['Contract Templates', '7 docs'],
          ].map(([label, count]) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between',
              padding: '5px 0', borderBottom: '1px solid var(--border)',
              fontSize: '0.78rem',
            }}>
              <span style={{ color: 'var(--text2)' }}>{label}</span>
              <span style={{ color: 'var(--brown)', fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>{count}</span>
            </div>
          ))}
          <div style={{ marginTop: 9, fontSize: '0.68rem', color: 'var(--text3)', lineHeight: 1.5 }}>
            Chunking: clause · Retrieval: hybrid RRF
          </div>
        </div>
      </div>
    </div>
  );
}