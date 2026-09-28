import React from 'react'

export function RecommendationPanel({
  recommendation,
  verificationPlan,
  onOpenRecordOutcome,
}) {
  if (!recommendation) return null

  return (
    <div className="glass-panel" style={{ padding: 28, border: '1px solid rgba(6, 182, 212, 0.25)' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 20,
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: 'linear-gradient(135deg, var(--cyan-500), var(--indigo-600))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>
              Outcome-Aware Recommendation
            </h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Synthesized by Hindsight Reflect over empirical quality history
            </span>
          </div>
        </div>

        <button
          className="btn btn-success"
          onClick={onOpenRecordOutcome}
          style={{ padding: '9px 18px' }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <polyline points="20 6 9 17 4 12" />
          </svg>
          Record Verification Outcome
        </button>
      </div>

      {/* Main Corrective Action Box */}
      <div style={{
        background: 'rgba(6, 182, 212, 0.05)',
        border: '1px solid rgba(6, 182, 212, 0.3)',
        borderRadius: 'var(--radius-md)',
        padding: 20,
        marginBottom: 20,
      }}>
        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--cyan-400)', fontWeight: 700, marginBottom: 6 }}>
          Recommended Corrective Action
        </div>
        <p style={{ fontSize: '1.05rem', color: '#fff', fontWeight: 500, lineHeight: 1.6 }}>
          {recommendation.corrective_action}
        </p>
      </div>

      {/* Why Relevant / Reason */}
      <div style={{ marginBottom: 24 }}>
        <h4 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
          Evidence Basis & Association Rationale:
        </h4>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: 1.6, background: 'rgba(255, 255, 255, 0.02)', padding: 14, borderRadius: 'var(--radius-md)' }}>
          {recommendation.reason}
        </p>
      </div>

      {/* Verification Plan */}
      {verificationPlan && verificationPlan.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
              Suggested Verification Plan
            </h4>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-dim)' }}>Must verify prior to recurrence closure</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {verificationPlan.map((step) => (
              <div
                key={step.step}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 14,
                  padding: '12px 16px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <span style={{
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  background: 'rgba(6, 182, 212, 0.15)',
                  color: 'var(--cyan-400)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  flexShrink: 0,
                }}>
                  {step.step}
                </span>

                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.9rem', fontWeight: 500, color: '#fff', marginBottom: 4 }}>
                    {step.action}
                  </div>
                  <div style={{ display: 'flex', gap: 16, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {step.duration && <span>⏱ Duration: <strong>{step.duration}</strong></span>}
                    {step.metric && <span>📊 Metric: <strong>{step.metric}</strong></span>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Limitations */}
      {recommendation.limitations && recommendation.limitations.length > 0 && (
        <div>
          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Empirical Limitations & Disclaimers:
          </h4>
          <ul style={{ paddingLeft: 20, fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            {recommendation.limitations.map((lim, idx) => (
              <li key={idx} style={{ marginBottom: 4 }}>
                {lim}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
