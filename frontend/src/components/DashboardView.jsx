import React from 'react'

export function DashboardView({ onNavigateAnalyze, onNavigateDemo, onSeed, isSeeding, bankId }) {
  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      {/* Hero Section */}
      <div className="glass-panel" style={{
        padding: '48px 40px',
        background: 'radial-gradient(ellipse 70% 80% at 50% 0%, rgba(30, 41, 67, 0.6), rgba(15, 22, 35, 0.95))',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          background: 'rgba(6, 182, 212, 0.1)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          padding: '6px 16px',
          borderRadius: 'var(--radius-full)',
          fontSize: '0.82rem',
          color: 'var(--cyan-400)',
          fontWeight: 600,
          marginBottom: 16,
        }}>
          <span>⚡ Hack With Hyderabad 3.0</span>
          <span>•</span>
          <span>Powered by Hindsight Cloud Memory</span>
        </div>

        <h1 style={{ fontSize: '2.8rem', fontWeight: 800, marginBottom: 16, lineHeight: 1.15 }}>
          Outcome-Aware Supplier<br />
          <span style={{
            background: 'linear-gradient(135deg, var(--cyan-400), #818cf8)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Corrective-Action Agent
          </span>
        </h1>

        <p style={{
          fontSize: '1.1rem',
          color: 'var(--text-muted)',
          maxWidth: 680,
          margin: '0 auto 32px auto',
          lineHeight: 1.6,
        }}>
          Supplier defects recur when quality teams fail to learn from past corrective actions and their measured verification outcomes. CAPAloop closes the loop using Hindsight memory.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: 16, flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            style={{ padding: '12px 28px', fontSize: '0.98rem' }}
            onClick={onNavigateAnalyze}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            Analyze New Defect
          </button>

          <button
            className="btn btn-secondary"
            style={{ padding: '12px 28px', fontSize: '0.98rem' }}
            onClick={onNavigateDemo}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            Interactive Judge Demo
          </button>
        </div>
      </div>

      {/* 3-Step Visual Architecture */}
      <div>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--cyan-400)' }}>
            The Continuous Closed Loop
          </span>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 700, marginTop: 4 }}>
            How CAPAloop Prevents Defect Recurrence
          </h2>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 20,
        }}>
          {/* Step 1: Recall */}
          <div className="glass-panel" style={{ padding: 28, position: 'relative' }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: 'rgba(6, 182, 212, 0.15)',
              color: 'var(--cyan-400)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              marginBottom: 16,
              border: '1px solid rgba(6, 182, 212, 0.3)',
            }}>
              1
            </div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: 8, color: '#fff' }}>
              RECALL
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>
              Searches Hindsight Cloud for similar historical defect cases, retrieving previous supplier actions, verification periods, and measured outcomes.
            </p>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              <span className="badge badge-grade-b">Evidence Grading A–D</span>
              <span className="badge badge-warning">Contradiction Detection</span>
            </div>
          </div>

          {/* Step 2: Recommend */}
          <div className="glass-panel" style={{ padding: 28, position: 'relative' }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: 'rgba(99, 102, 241, 0.15)',
              color: 'var(--indigo-400)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              marginBottom: 16,
              border: '1px solid rgba(99, 102, 241, 0.3)',
            }}>
              2
            </div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: 8, color: '#fff' }}>
              RECOMMEND
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>
              Synthesizes Hindsight reflection over empirical precedents to suggest actionable CAPA steps. Strictly uses non-causal association wording.
            </p>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              <span className="badge badge-grade-a">Actionable Plan</span>
              <span className="badge badge-purple">No False Causality</span>
            </div>
          </div>

          {/* Step 3: Learn */}
          <div className="glass-panel" style={{ padding: 28, position: 'relative' }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: 'rgba(16, 185, 129, 0.15)',
              color: 'var(--emerald-400)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              marginBottom: 16,
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}>
              3
            </div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: 8, color: '#fff' }}>
              LEARN
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>
              Following verification period, before/after metrics and recurrence outcomes are retained in Hindsight Cloud. Future analyses immediately benefit.
            </p>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              <span className="badge badge-success">Closed-Loop Memory</span>
              <span className="badge badge-grade-a">Audit Trail</span>
            </div>
          </div>
        </div>
      </div>

      {/* Domain Context & Precedent Seeding Banner */}
      <div className="glass-panel" style={{
        padding: '24px 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 20,
        background: 'rgba(15, 23, 42, 0.6)',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>
              Hindsight Bank: <code className="font-mono" style={{ color: 'var(--cyan-400)', background: 'rgba(6, 182, 212, 0.1)', padding: '2px 8px', borderRadius: 4 }}>{bankId || 'supplier-quality-capa'}</code>
            </span>
            <span className="badge badge-success">Live Cloud Memory</span>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', maxWidth: 640 }}>
            Contains verified supplier-quality experiences across stamping, casting, machining, and electronics manufacturing.
          </p>
        </div>

        <button
          className="btn btn-secondary"
          onClick={onSeed}
          disabled={isSeeding}
        >
          {isSeeding ? (
            <>
              <span className="spinner" style={{ width: 14, height: 14 }} />
              <span>Seeding 10 Synthetic Cases...</span>
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Reset / Reseed Synthetic Bank</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}
