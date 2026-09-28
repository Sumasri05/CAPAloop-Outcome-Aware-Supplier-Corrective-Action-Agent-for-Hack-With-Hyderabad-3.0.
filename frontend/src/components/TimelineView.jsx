import React, { useState, useEffect } from 'react'
import { api } from '../api/client'

const LIFECYCLE_STAGES = [
  { id: 1, title: 'Defect Detected', desc: 'Supplier part inspection flags anomaly' },
  { id: 2, title: 'Evidence Recalled', desc: 'Hindsight searches historical precedents' },
  { id: 3, title: 'Recommendation Generated', desc: 'Reflect synthesizes outcome-aware CAPA' },
  { id: 4, title: 'Action Implemented', desc: 'Supplier applies recommended adjustment' },
  { id: 5, title: 'Outcome Verified', desc: 'Before/after defect rate metrics captured' },
  { id: 6, title: 'Retained in Memory', desc: 'Hindsight bank permanently records lesson' },
]

export function TimelineView({ selectedDefectId }) {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadTimeline = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getTimeline(selectedDefectId)
      setEvents(data.events || [])
    } catch (err) {
      setError(err.message || 'Failed to fetch timeline')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTimeline()
  }, [selectedDefectId])

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      {/* Visual Defect Lifecycle Flowchart */}
      <div className="glass-panel" style={{ padding: 28 }}>
        <div style={{ marginBottom: 20 }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>
            Closed-Loop CAPA Lifecycle
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            How organizational learning flows from detection to permanent Hindsight Cloud retention.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 12,
          position: 'relative',
        }}>
          {LIFECYCLE_STAGES.map((s, idx) => (
            <div
              key={s.id}
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: 16,
                position: 'relative',
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                marginBottom: 8,
              }}>
                <span style={{
                  width: 22,
                  height: 22,
                  borderRadius: '50%',
                  background: 'rgba(6, 182, 212, 0.15)',
                  color: 'var(--cyan-400)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                }}>
                  {s.id}
                </span>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>
                  {s.title}
                </span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.4 }}>
                {s.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Live Timeline Audit Trail */}
      <div className="glass-panel" style={{ padding: 28 }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 20,
          flexWrap: 'wrap',
          gap: 12,
        }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>
              Live Event Audit Log
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {selectedDefectId ? (
                <>Filtering for defect: <code className="font-mono" style={{ color: 'var(--cyan-400)' }}>{selectedDefectId}</code></>
              ) : (
                'All recent system learning events (newest first)'
              )}
            </span>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={loadTimeline}
            disabled={loading}
          >
            {loading ? <span className="spinner" style={{ width: 12, height: 12 }} /> : '↻ Refresh Log'}
          </button>
        </div>

        {error && (
          <div className="alert alert-warning">
            Error loading timeline: {error}
          </div>
        )}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
            <span className="spinner" style={{ width: 24, height: 24, marginBottom: 12 }} /><br />
            Loading timeline events...
          </div>
        ) : events.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '48px 16px',
            background: 'rgba(255, 255, 255, 0.01)',
            borderRadius: 'var(--radius-md)',
            border: '1px dashed var(--border-subtle)',
            color: 'var(--text-muted)',
            fontSize: '0.9rem',
          }}>
            No events recorded yet. Submit a defect analysis or record an outcome to view live audit entries.
          </div>
        ) : (
          <div style={{
            position: 'relative',
            paddingLeft: 24,
            borderLeft: '2px solid rgba(6, 182, 212, 0.25)',
            display: 'flex',
            flexDirection: 'column',
            gap: 20,
          }}>
            {events.map((evt, idx) => {
              const isRetained = evt.event_type === 'experience_retained'
              const isOutcome = evt.event_type === 'outcome_recorded'
              const isAnalysis = evt.event_type === 'defect_analyzed'

              const dotColor = isRetained
                ? 'var(--emerald-400)'
                : isOutcome
                ? 'var(--cyan-400)'
                : 'var(--indigo-400)'

              return (
                <div key={idx} style={{ position: 'relative' }}>
                  {/* Timeline Node Dot */}
                  <span style={{
                    position: 'absolute',
                    left: -31,
                    top: 4,
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    background: dotColor,
                    boxShadow: `0 0 10px ${dotColor}`,
                  }} />

                  <div style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '14px 18px',
                  }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: 6,
                      flexWrap: 'wrap',
                      gap: 8,
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span className={`badge ${
                          isRetained ? 'badge-success' : isOutcome ? 'badge-grade-b' : 'badge-grade-c'
                        }`}>
                          {evt.event_type.replace('_', ' ')}
                        </span>
                        <code className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>
                          {evt.experience_id}
                        </code>
                      </div>

                      <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                        {new Date(evt.timestamp).toLocaleTimeString()} • {new Date(evt.timestamp).toLocaleDateString()}
                      </span>
                    </div>

                    <p style={{ fontSize: '0.86rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                      {evt.summary}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
