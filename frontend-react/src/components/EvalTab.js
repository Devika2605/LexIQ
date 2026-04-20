import React, { useState, useEffect } from 'react';

const API = 'http://localhost:8000';

// /results returns { experiments: [...] }  (NOT results:[])
// Each item: { strategy, retriever, faithfulness, answer_relevancy, context_precision, context_recall }

const FINDINGS = [
  { level: 'HIGH',   text: 'BM25 sparse retrieval underperforms due to vocabulary mismatch between user questions and Indian legal terminology.' },
  { level: 'MEDIUM', text: 'Dense retrieval beats hybrid — the sparse component pulls hybrid scores down.' },
  { level: 'LOW',    text: 'Query expansion fixed Q07 (minor contracts) and Q10 (NDA) from 0.00 to meaningful scores.' },
  { level: 'LOW',    text: 'Dominant failure mode is retrieval (wrong chunks), not LLM hallucination — invest in query expansion, not prompt engineering.' },
];

const RISK_COLOR = { HIGH: 'var(--red)', MEDIUM: 'var(--amber)', LOW: 'var(--green)' };
const RISK_BG    = { HIGH: 'var(--red-bg)', MEDIUM: 'var(--amber-bg)', LOW: 'var(--green-bg)' };

function Bar({ value, max, best }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ flex: 1, height: 5, background: 'var(--bg3)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          width: `${pct}%`, height: '100%',
          background: best ? 'var(--brown)' : 'var(--brown-lt)',
          borderRadius: 3, transition: 'width 0.5s ease',
        }} />
      </div>
      <span style={{
        fontSize: '0.74rem', fontFamily: 'var(--font-mono)',
        color: best ? 'var(--brown)' : 'var(--text2)', minWidth: 40, fontWeight: best ? 700 : 400,
      }}>{value.toFixed(3)}</span>
    </div>
  );
}

// Demo data shown when API is offline
const DEMO = [
  { strategy: 'fixed',     retriever: 'dense',  faithfulness: 0.598, answer_relevancy: 0.721, context_precision: 0.643, context_recall: 0.584 },
  { strategy: 'fixed',     retriever: 'hybrid', faithfulness: 0.547, answer_relevancy: 0.689, context_precision: 0.612, context_recall: 0.541 },
  { strategy: 'recursive', retriever: 'dense',  faithfulness: 0.488, answer_relevancy: 0.651, context_precision: 0.573, context_recall: 0.512 },
  { strategy: 'clause',    retriever: 'dense',  faithfulness: 0.471, answer_relevancy: 0.620, context_precision: 0.548, context_recall: 0.498 },
  { strategy: 'fixed',     retriever: 'sparse', faithfulness: 0.310, answer_relevancy: 0.498, context_precision: 0.412, context_recall: 0.378 },
];

export default function EvalTab() {
  const [data, setData] = useState(null);       // experiments array
  const [loading, setLoading] = useState(false);
  const [offline, setOffline] = useState(false);

  useEffect(() => { load(); }, []);

  const load = async () => {
    setLoading(true); setOffline(false);
    try {
      const res = await fetch(`${API}/results`);
      if (!res.ok) throw new Error('no results');
      const json = await res.json();
      // API returns { experiments: [...] }
      setData(json.experiments || []);
    } catch {
      setData(DEMO);
      setOffline(true);
    }
    setLoading(false);
  };

  const experiments = data || [];
  const best  = experiments.length ? experiments.reduce((a, b) => a.faithfulness > b.faithfulness ? a : b) : null;
  const worst = experiments.length ? experiments.reduce((a, b) => a.faithfulness < b.faithfulness ? a : b) : null;
  const maxF  = best?.faithfulness || 1;
  const improvement = best && worst && worst.faithfulness > 0
    ? ((best.faithfulness - worst.faithfulness) / worst.faithfulness * 100).toFixed(0)
    : '—';

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

      {/* Header */}
      <div style={{
        padding: '16px 26px 12px', borderBottom: '1px solid var(--border)',
        flexShrink: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
      }}>
        <div>
          <div style={{ fontFamily: 'var(--font-serif)', fontSize: '1.4rem', fontWeight: 600, color: 'var(--text)' }}>
            Eval Results
          </div>
          <div style={{ fontSize: '0.73rem', color: 'var(--text3)', marginTop: 2 }}>
            9 experiments · 51 hand-curated Q&A pairs · custom Groq RAGAS scoring
          </div>
        </div>
        <button onClick={load} style={{
          background: 'transparent', border: '1px solid var(--border)',
          borderRadius: 6, padding: '5px 12px', fontSize: '0.74rem', color: 'var(--text3)',
        }}>↺ Refresh</button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '22px 26px' }}>

        {/* Offline notice */}
        {offline && (
          <div style={{
            background: 'var(--amber-bg)', border: '1px solid rgba(146,64,14,0.18)',
            borderRadius: 8, padding: '9px 14px', marginBottom: 16,
            fontSize: '0.78rem', color: 'var(--amber)',
          }}>
            API offline — showing demo data. Run: <code style={{ fontFamily: 'var(--font-mono)' }}>python api/main.py</code>
          </div>
        )}

        {loading && (
          <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text3)', fontSize: '0.85rem' }}>
            Loading results…
          </div>
        )}

        {/* Stat cards */}
        {experiments.length > 0 && (
          <div style={{ display: 'flex', gap: 10, marginBottom: 22 }}>
            {[
              { label: 'Best Config',    value: best  ? `${best.strategy} + ${best.retriever}`   : '—', sub: best  ? `↑ ${best.faithfulness.toFixed(3)}`  : '', color: 'var(--green)' },
              { label: 'Worst Config',   value: worst ? `${worst.strategy} + ${worst.retriever}` : '—', sub: worst ? `↓ ${worst.faithfulness.toFixed(3)}` : '', color: 'var(--red)' },
              { label: 'Improvement',   value: `${improvement}%`, sub: 'worst → best faithfulness', color: 'var(--brown)' },
              { label: 'Test Questions',value: '51',  sub: 'hand-curated Indian law Q&A',          color: 'var(--text2)' },
            ].map(({ label, value, sub, color }) => (
              <div key={label} style={{
                flex: 1, background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: 10, padding: '12px 14px',
              }}>
                <div style={{ fontSize: '0.63rem', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.09em', marginBottom: 5 }}>
                  {label}
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color, fontFamily: 'var(--font-mono)', lineHeight: 1.2 }}>
                  {value}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text3)', marginTop: 3 }}>{sub}</div>
              </div>
            ))}
          </div>
        )}

        {/* Experiments table */}
        {experiments.length > 0 && (
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 12, overflow: 'hidden', marginBottom: 22,
          }}>
            <div style={{
              padding: '12px 18px', borderBottom: '1px solid var(--border)',
              fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 600, color: 'var(--text)',
            }}>Experiment Comparison</div>

            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: 'var(--bg2)' }}>
                  {['Chunking', 'Retriever', 'Faithfulness', 'Ans. Rel.', 'Ctx. Prec.', 'Ctx. Rec.'].map(h => (
                    <th key={h} style={{
                      padding: '9px 14px', textAlign: 'left',
                      fontSize: '0.65rem', color: 'var(--text3)',
                      textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600,
                      borderBottom: '1px solid var(--border)',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {experiments.map((r, i) => {
                  const isBest = r.faithfulness === best?.faithfulness;
                  return (
                    <tr key={i} style={{
                      background: isBest ? 'rgba(107,58,31,0.04)' : 'transparent',
                      borderBottom: '1px solid var(--border)',
                    }}>
                      <td style={{ padding: '11px 14px' }}>
                        <span style={{
                          background: 'var(--bg2)', border: '1px solid var(--border)',
                          borderRadius: 4, padding: '2px 9px',
                          fontSize: '0.73rem', fontFamily: 'var(--font-mono)',
                          color: isBest ? 'var(--brown)' : 'var(--text2)',
                          fontWeight: isBest ? 700 : 400,
                        }}>{r.strategy}</span>
                        {isBest && <span style={{ marginLeft: 5, fontSize: '0.68rem', color: 'var(--brown)' }}>★</span>}
                      </td>
                      <td style={{ padding: '11px 14px', fontSize: '0.8rem', color: 'var(--text2)' }}>{r.retriever}</td>
                      <td style={{ padding: '11px 14px', minWidth: 150 }}>
                        <Bar value={r.faithfulness || 0} max={maxF} best={isBest} />
                      </td>
                      <td style={{ padding: '11px 14px', fontSize: '0.75rem', color: 'var(--text2)', fontFamily: 'var(--font-mono)' }}>
                        {(r.answer_relevancy || 0).toFixed(4)}
                      </td>
                      <td style={{ padding: '11px 14px', fontSize: '0.75rem', color: 'var(--text2)', fontFamily: 'var(--font-mono)' }}>
                        {(r.context_precision || 0).toFixed(4)}
                      </td>
                      <td style={{ padding: '11px 14px', fontSize: '0.75rem', color: 'var(--text2)', fontFamily: 'var(--font-mono)' }}>
                        {(r.context_recall || 0).toFixed(4)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* No results */}
        {!loading && experiments.length === 0 && !offline && (
          <div style={{
            background: 'var(--surface)', border: '1px solid var(--border)',
            borderRadius: 12, padding: 36, textAlign: 'center',
          }}>
            <div style={{ fontSize: '0.9rem', color: 'var(--text2)', marginBottom: 6 }}>No results yet</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text3)', fontFamily: 'var(--font-mono)' }}>
              python evaluation/ragas_eval.py
            </div>
          </div>
        )}

        {/* Key findings */}
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 12, overflow: 'hidden', marginBottom: 18,
        }}>
          <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--border)', fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 600, color: 'var(--text)' }}>
            Key Findings
          </div>
          <div style={{ padding: '14px 18px' }}>
            {FINDINGS.map(({ level, text }, i) => (
              <div key={i} style={{
                display: 'flex', gap: 10, alignItems: 'flex-start',
                padding: '9px 0',
                borderBottom: i < FINDINGS.length - 1 ? '1px solid var(--border)' : 'none',
              }}>
                <span style={{
                  background: RISK_BG[level], color: RISK_COLOR[level],
                  fontSize: '0.6rem', fontWeight: 700, padding: '2px 7px', borderRadius: 3,
                  flexShrink: 0, marginTop: 2, letterSpacing: '0.04em',
                }}>{level}</span>
                <span style={{ fontSize: '0.81rem', color: 'var(--text2)', lineHeight: 1.6 }}>{text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Failure analysis */}
        <div style={{
          background: 'var(--surface)', border: '1px solid var(--border)',
          borderRadius: 12, overflow: 'hidden',
        }}>
          <div style={{ padding: '12px 18px', borderBottom: '1px solid var(--border)', fontFamily: 'var(--font-serif)', fontSize: '1rem', fontWeight: 600, color: 'var(--text)' }}>
            Failure Analysis — Top 10 Cases
          </div>
          <div style={{ padding: '16px 18px' }}>
            {[
              { label: 'Wrong chunk retrieved',  count: 4, pct: 40, level: 'HIGH' },
              { label: 'Chunk boundary split',    count: 3, pct: 30, level: 'MEDIUM' },
              { label: 'Out of corpus',           count: 2, pct: 20, level: 'MEDIUM' },
              { label: 'LLM hallucination',       count: 1, pct: 10, level: 'LOW' },
            ].map(({ label, count, pct, level }) => (
              <div key={label} style={{ marginBottom: 13 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text2)' }}>{label}</span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text3)', fontFamily: 'var(--font-mono)' }}>{count}/10</span>
                </div>
                <div style={{ height: 5, background: 'var(--bg3)', borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{
                    height: '100%', width: `${pct}%`, borderRadius: 3,
                    background: RISK_COLOR[level], transition: 'width 0.5s ease',
                  }} />
                </div>
              </div>
            ))}
            <div style={{
              marginTop: 12, padding: '9px 12px',
              background: 'var(--brown-dim)', border: '1px solid var(--border2)',
              borderRadius: 8, fontSize: '0.78rem', color: 'var(--text2)', lineHeight: 1.6,
            }}>
              <strong style={{ color: 'var(--brown)' }}>Insight:</strong> 70% of failures are retrieval failures, not generation failures. Invest in query expansion and re-ranking, not prompt engineering.
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}