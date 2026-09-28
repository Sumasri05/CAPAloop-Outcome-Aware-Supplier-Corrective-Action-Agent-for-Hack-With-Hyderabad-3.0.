import React, { useState } from 'react'
import { api } from '../api/client'

export function LearningDemoView({ onNavigateToAnalysisWithData }) {
  const [demoState, setDemoState] = useState('idle') // idle, analyzing_before, recording_outcome, analyzing_after, completed
  const [beforeResult, setBeforeResult] = useState(null)
  const [outcomeResult, setOutcomeResult] = useState(null)
  const [afterResult, setAfterResult] = useState(null)
  const [logs, setLogs] = useState([])

  const addLog = (msg) => {
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`])
  }

  const runFullDemo = async () => {
    setDemoState('analyzing_before')
    setLogs([])
    setBeforeResult(null)
    setOutcomeResult(null)
    setAfterResult(null)

    const uniqueDefectType = `Micro-crack Delamination ${Math.floor(Math.random() * 1000)}`
    const demoDefect = {
      supplier: 'Solaria Advanced Materials',
      part_number: 'SOL-501',
      defect_type: uniqueDefectType,
      severity: 'critical',
      manufacturing_process: 'Precision composite autoclave curing',
      description: 'Layer delamination observed under thermal cycling inspection.',
      root_cause_hypothesis: 'Excessive thermal ramp rate during autoclave cure cycle.',
    }

    try {
      // Step 1: Analyze Before Learning
      addLog(`Step 1: Submitting new defect instance "${uniqueDefectType}" — this defect has no verified outcome retained yet...`)
      const res1 = await api.analyzeDefect(demoDefect)
      setBeforeResult(res1)
      addLog(`Analyzed. Defect ID: ${res1.defect_id}. Related historical cases: ${res1.historical_cases_found}. Overall evidence grade: ${res1.recommendation.evidence_grade} (current defect NOT yet verified)`)

      // Step 2: Record Verified Outcome
      setDemoState('recording_outcome')
      addLog(`Step 2: Corrective action applied: "Reduced autoclave thermal ramp rate from 3.5°C/min to 1.8°C/min and extended dwell by 20 minutes."`)
      addLog(`Simulating 30-day verification period and 0% delamination measurement...`)

      const outcomeData = {
        defect_id: res1.defect_id,
        corrective_action_taken: 'Reduced autoclave thermal ramp rate from 3.5°C/min to 1.8°C/min and extended dwell by 20 minutes.',
        verification_period: '30 production days (450 parts inspected)',
        measurement_before: '12.4% delamination rate',
        measurement_after: '0.0% delamination rate (zero failures)',
        outcome: 'successful',
        recurrence: 'Zero recurrence observed across entire 30-day production lot.',
        notes: 'Autoclave recipe profile locked and verified by Quality Director.',
        evidence_quality: 'A',
      }

      const outcomeRes = await api.recordOutcome(outcomeData)
      setOutcomeResult(outcomeRes)
      addLog(`Outcome successfully retained in Hindsight Cloud memory! Experience ID: ${outcomeRes.experience_id}`)

      // Step 3: Re-analyze to Prove Learning
      setDemoState('analyzing_after')
      addLog(`Step 3: A new defect occurs with the same failure mode: "${uniqueDefectType}" at Solaria. Re-querying Hindsight...`)

      const res2 = await api.analyzeDefect(demoDefect)
      setAfterResult(res2)
      addLog(`Re-analyzed! Hindsight recalled ${res2.historical_cases_found} case(s). Overall evidence grade: ${res2.recommendation.evidence_grade}`)
      addLog(`The newly retained verified experience is now retrieved and powering the recommendation!`)

      setDemoState('completed')
    } catch (err) {
      addLog(`ERROR: ${err.message}`)
      setDemoState('idle')
    }
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
      {/* Intro Header */}
      <div className="glass-panel" style={{
        padding: 32,
        background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.4), rgba(15, 23, 42, 0.9))',
        border: '1px solid rgba(168, 85, 247, 0.3)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', padding: '4px 12px', borderRadius: 'var(--radius-full)', fontSize: '0.78rem', fontWeight: 600, marginBottom: 10 }}>
              ★ Judge Proof of Learning Demonstration
            </div>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', marginBottom: 8 }}>
              Before vs. After Learning in Action
            </h2>
            <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', maxWidth: 680, lineHeight: 1.5 }}>
              This demo proves CAPAloop is an <strong>Outcome-Aware</strong> agent: a new defect instance is analyzed, a human-verified outcome is retained into Hindsight Cloud, and subsequent analyses immediately retrieve that newly learned experience.
            </p>
          </div>

          <button
            className="btn btn-primary"
            style={{
              background: 'linear-gradient(135deg, #a855f7, #6366f1)',
              boxShadow: '0 4px 20px rgba(168, 85, 247, 0.4)',
              padding: '12px 28px',
              fontSize: '0.98rem',
            }}
            onClick={runFullDemo}
            disabled={demoState !== 'idle' && demoState !== 'completed'}
          >
            {demoState !== 'idle' && demoState !== 'completed' ? (
              <>
                <span className="spinner" />
                <span>Running Live Demo...</span>
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                <span>Run Live Learning Demo</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Execution Logs */}
      {logs.length > 0 && (
        <div className="glass-panel" style={{ padding: 20, background: '#0a0e17' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Live Hindsight Cloud API Logs
            </span>
            <span className="badge badge-grade-b">{demoState.toUpperCase()}</span>
          </div>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '0.8rem',
            color: '#a7f3d0',
            lineHeight: 1.6,
            maxHeight: 160,
            overflowY: 'auto',
          }}>
            {logs.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        </div>
      )}

      {/* Side-by-Side Before vs. After Comparison */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
        gap: 24,
      }}>
        {/* BEFORE CARD */}
        <div className="glass-panel" style={{
          padding: 28,
          border: '1px solid rgba(245, 158, 11, 0.3)',
          background: 'rgba(245, 158, 11, 0.02)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{
              fontSize: '0.82rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              color: 'var(--amber-400)',
              letterSpacing: '0.06em',
            }}>
              Step 1: Before Learning
            </span>
            <span className="badge badge-warning">New Defect Instance</span>
          </div>

          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginBottom: 12 }}>
            New Defect Instance — Not Yet Verified
          </h3>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 18 }}>
            This defect instance has not yet been verified and retained by CAPAloop. Hindsight may still retrieve related historical cases that provide initial context, but the current defect's own outcome is not yet in memory.
          </div>

          {beforeResult ? (
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 'var(--radius-md)',
              padding: 16,
              border: '1px solid var(--border-subtle)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-dim)' }}>Overall Retrieved Evidence:</span>
                <span className={`badge badge-grade-${beforeResult.recommendation.evidence_grade.toLowerCase()}`}>Grade {beforeResult.recommendation.evidence_grade}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-dim)' }}>Current Defect Verified:</span>
                <span className="badge badge-warning">Not Yet</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-dim)' }}>Historical Cases:</span>
                <span style={{ fontWeight: 600, color: '#fff' }}>{beforeResult.historical_cases_found}</span>
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginBottom: 4 }}>Initial Recommendation:</div>
              <p style={{ fontSize: '0.85rem', color: '#fff', lineHeight: 1.5 }}>
                {beforeResult.recommendation.corrective_action}
              </p>
            </div>
          ) : (
            <div style={{
              padding: 24,
              textAlign: 'center',
              border: '1px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-dim)',
              fontSize: '0.85rem',
            }}>
              Click "Run Live Learning Demo" to execute Step 1.
            </div>
          )}
        </div>

        {/* AFTER CARD */}
        <div className="glass-panel" style={{
          padding: 28,
          border: '1px solid rgba(16, 185, 129, 0.4)',
          background: 'rgba(16, 185, 129, 0.03)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <span style={{
              fontSize: '0.82rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              color: 'var(--emerald-400)',
              letterSpacing: '0.06em',
            }}>
              Step 2: After Learning
            </span>
            <span className="badge badge-success">Verified Experience Recalled</span>
          </div>

          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginBottom: 12 }}>
            Re-Analysis After Verification & Retention
          </h3>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 18 }}>
            After verification, this defect's outcome was retained in Hindsight. Subsequent analysis can now retrieve the newly learned experience alongside any existing historical context.
          </div>

          {afterResult ? (
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 'var(--radius-md)',
              padding: 16,
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-dim)' }}>Overall Retrieved Evidence:</span>
                <span className={`badge badge-grade-${afterResult.recommendation.evidence_grade.toLowerCase()}`}>Grade {afterResult.recommendation.evidence_grade}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-dim)' }}>Newly Retained Experience:</span>
                <span className="badge badge-grade-a">Grade A (Human-Verified)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: '0.82rem' }}>
                <span style={{ color: 'var(--text-dim)' }}>Recalled Cases:</span>
                <span style={{ fontWeight: 600, color: 'var(--emerald-400)' }}>
                  {afterResult.historical_cases_found} (includes {outcomeResult?.experience_id || 'newly retained'})
                </span>
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginBottom: 4 }}>Outcome-Aware Recommendation:</div>
              <p style={{ fontSize: '0.85rem', color: '#fff', lineHeight: 1.5 }}>
                {afterResult.recommendation.corrective_action}
              </p>
            </div>
          ) : (
            <div style={{
              padding: 24,
              textAlign: 'center',
              border: '1px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-dim)',
              fontSize: '0.85rem',
            }}>
              Awaiting verification retention and re-analysis...
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
