import React from 'react'

const GRADE_CONFIG = {
  A: {
    label: 'A — Strong Evidence',
    badgeClass: 'badge-grade-a',
    desc: 'Empirically verified outcome, adequate verification period, zero recurrence.',
  },
  B: {
    label: 'B — Moderate Evidence',
    badgeClass: 'badge-grade-b',
    desc: 'Verified outcome with minor caveats or limited observation duration.',
  },
  C: {
    label: 'C — Weak Evidence',
    badgeClass: 'badge-grade-c',
    desc: 'Unverified intervention, inconsistent measurement, or conflicting data.',
  },
  D: {
    label: 'D — Insufficient Precedent',
    badgeClass: 'badge-grade-d',
    desc: 'No usable precedent located in Hindsight memory for this failure mode.',
  },
}

const OUTCOME_CONFIG = {
  successful: { label: 'Successful', badgeClass: 'badge-success' },
  partial: { label: 'Partial Resolution', badgeClass: 'badge-warning' },
  failed: { label: 'Failed Outcome', badgeClass: 'badge-danger' },
  recurrence: { label: 'Recurrence Detected', badgeClass: 'badge-purple' },
}

export function EvidencePanel({ cases, contradictions, overallGrade }) {
  const gradeInfo = GRADE_CONFIG[overallGrade] || GRADE_CONFIG.D

  return (
    <div className="glass-panel" style={{ padding: 24 }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 16,
        flexWrap: 'wrap',
        gap: 12,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>
            Historical Evidence Recalled
          </h3>
          <span style={{
            background: 'rgba(255, 255, 255, 0.08)',
            color: 'var(--cyan-400)',
            padding: '2px 8px',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.78rem',
            fontWeight: 600,
          }}>
            {cases.length} {cases.length === 1 ? 'Case' : 'Cases'} Found
          </span>
        </div>

        {/* Overall Grade Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Precedent Quality:</span>
          <span className={`badge ${gradeInfo.badgeClass}`} style={{ fontSize: '0.8rem', padding: '4px 10px' }}>
            {gradeInfo.label}
          </span>
        </div>
      </div>

      {/* Non-Causality Disclaimer Alert */}
      <div className="alert alert-info" style={{ marginBottom: 18 }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0, marginTop: 1 }}>
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <div style={{ fontSize: '0.82rem', lineHeight: 1.5 }}>
          <strong>Association Guardrail:</strong> Historical precedents indicate corrective actions that were <em>associated</em> with specific outcomes in past contexts. Association does not establish absolute causation or guarantee future performance.
        </div>
      </div>

      {/* Contradictory Evidence Alert if any */}
      {contradictions && contradictions.length > 0 && (
        <div className="alert alert-warning" style={{ marginBottom: 18 }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ flexShrink: 0, marginTop: 1 }}>
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <div>
            <strong style={{ display: 'block', marginBottom: 4 }}>Contradictory Precedents Detected:</strong>
            <ul style={{ paddingLeft: 18, fontSize: '0.82rem' }}>
              {contradictions.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Cases List */}
      {cases.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '32px 16px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: 'var(--radius-md)',
          border: '1px dashed var(--border-subtle)',
        }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 6 }}>
            No prior historical experiences found in Hindsight memory for this specific defect profile.
          </p>
          <span className="badge badge-grade-d">Grade D — No usable precedent</span>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {cases.map((c, index) => {
            const outcomeStyle = OUTCOME_CONFIG[c.outcome?.toLowerCase()] || {
              label: c.outcome || 'Unknown',
              badgeClass: 'badge-grade-b',
            }
            const caseGrade = GRADE_CONFIG[c.evidence_grade?.toUpperCase()] || GRADE_CONFIG.B

            return (
              <div
                key={c.experience_id || index}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: 16,
                  transition: 'border-color 0.2s ease',
                }}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 8,
                  flexWrap: 'wrap',
                  gap: 8,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <code className="font-mono" style={{
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      color: 'var(--cyan-400)',
                      background: 'rgba(6, 182, 212, 0.1)',
                      padding: '2px 8px',
                      borderRadius: 4,
                    }}>
                      {c.experience_id}
                    </code>
                    <span className={`badge ${outcomeStyle.badgeClass}`}>
                      {outcomeStyle.label}
                    </span>
                  </div>

                  <span className={`badge ${caseGrade.badgeClass}`}>
                    Grade {c.evidence_grade}
                  </span>
                </div>

                <p style={{ fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                  {c.summary}
                </p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
