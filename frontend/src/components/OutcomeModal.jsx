import React, { useState } from 'react'

export function OutcomeModal({
  isOpen,
  onClose,
  defectId,
  recommendedAction,
  onSubmitOutcome,
  isSubmitting,
  submitResult,
  onTestLearning,
}) {
  const [formData, setFormData] = useState({
    corrective_action_taken: recommendedAction || 'Adjusted forming pressure to 380 kN and added first-article inspection.',
    verification_period: '14 production days',
    measurement_before: '7.8% defect rate',
    measurement_after: '0.8% defect rate',
    outcome: 'successful',
    recurrence: 'No recurrence observed during 14-day verification run.',
    notes: 'Tooling recalibrated and operator certified on new setup.',
    evidence_quality: 'A',
  })

  // Synchronize when recommendedAction changes
  React.useEffect(() => {
    if (recommendedAction) {
      setFormData((prev) => ({
        ...prev,
        corrective_action_taken: recommendedAction,
      }))
    }
  }, [recommendedAction])

  if (!isOpen) return null

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmitOutcome({
      ...formData,
      defect_id: defectId,
    })
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(5, 8, 15, 0.8)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: 20,
    }}>
      <div className="glass-panel animate-fade-in" style={{
        maxWidth: 680,
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: 32,
        background: '#0f1626',
        border: '1px solid rgba(16, 185, 129, 0.35)',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(16, 185, 129, 0.2)',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div>
            <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#fff' }}>
              Record Verification Outcome
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Defect: <code className="font-mono" style={{ color: 'var(--cyan-400)' }}>{defectId}</code> • Retains empirical outcome to Hindsight memory
            </p>
          </div>
          <button
            onClick={onClose}
            className="btn btn-secondary btn-sm"
            style={{ borderRadius: '50%', width: 32, height: 32, padding: 0 }}
          >
            ✕
          </button>
        </div>

        {/* Success View */}
        {submitResult && submitResult.hindsight_retained ? (
          <div style={{ textAlign: 'center', padding: '24px 12px' }}>
            <div style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              background: 'rgba(16, 185, 129, 0.2)',
              color: 'var(--emerald-400)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px auto',
              fontSize: '2rem',
              border: '2px solid var(--emerald-400)',
            }}>
              ✓
            </div>

            <h4 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', marginBottom: 8 }}>
              Verified Outcome Learned by CAPAloop!
            </h4>

            <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', maxWidth: 480, margin: '0 auto 20px auto', lineHeight: 1.6 }}>
              The verification outcome for <code className="font-mono" style={{ color: 'var(--cyan-400)' }}>{defectId}</code> has been successfully retained in Hindsight Cloud. Future analyses will now recall this experience as historical precedent.
            </p>

            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 'var(--radius-md)',
              padding: 16,
              marginBottom: 24,
              textAlign: 'left',
              fontSize: '0.82rem',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ color: 'var(--text-dim)' }}>Hindsight Retention:</span>
                <span className="badge badge-success">Live Stored</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ color: 'var(--text-dim)' }}>Experience ID:</span>
                <span className="font-mono" style={{ color: 'var(--cyan-400)' }}>{submitResult.experience_id}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-dim)' }}>Measured Improvement:</span>
                <span style={{ color: 'var(--emerald-400)', fontWeight: 600 }}>{formData.measurement_before} → {formData.measurement_after}</span>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: 12 }}>
              <button
                className="btn btn-primary"
                onClick={onTestLearning}
                style={{ padding: '10px 24px' }}
              >
                ★ Test Learning: Analyze Similar Defect
              </button>
              <button
                className="btn btn-secondary"
                onClick={onClose}
              >
                Close
              </button>
            </div>
          </div>
        ) : (
          /* Input Form */
          <form onSubmit={handleSubmit}>
            {/* Corrective Action Taken */}
            <div className="form-group">
              <label className="form-label">
                <span>Corrective Action Taken *</span>
              </label>
              <textarea
                name="corrective_action_taken"
                className="form-textarea"
                rows="2"
                value={formData.corrective_action_taken}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              />
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: 14,
            }}>
              {/* Verification Period */}
              <div className="form-group">
                <label className="form-label">
                  <span>Verification Period *</span>
                </label>
                <input
                  type="text"
                  name="verification_period"
                  className="form-input"
                  value={formData.verification_period}
                  onChange={handleChange}
                  placeholder="e.g. 14 production days"
                  required
                  disabled={isSubmitting}
                />
              </div>

              {/* Outcome */}
              <div className="form-group">
                <label className="form-label">
                  <span>Measured Outcome *</span>
                </label>
                <select
                  name="outcome"
                  className="form-select"
                  value={formData.outcome}
                  onChange={handleChange}
                  required
                  disabled={isSubmitting}
                >
                  <option value="successful">Successful (Resolved)</option>
                  <option value="partial">Partial Resolution</option>
                  <option value="failed">Failed (Unresolved)</option>
                  <option value="recurrence">Recurrence Observed</option>
                </select>
              </div>

              {/* Measurement Before */}
              <div className="form-group">
                <label className="form-label">
                  <span>Measurement Before *</span>
                </label>
                <input
                  type="text"
                  name="measurement_before"
                  className="form-input"
                  value={formData.measurement_before}
                  onChange={handleChange}
                  placeholder="e.g. 7.8% defect rate"
                  required
                  disabled={isSubmitting}
                />
              </div>

              {/* Measurement After */}
              <div className="form-group">
                <label className="form-label">
                  <span>Measurement After *</span>
                </label>
                <input
                  type="text"
                  name="measurement_after"
                  className="form-input"
                  value={formData.measurement_after}
                  onChange={handleChange}
                  placeholder="e.g. 0.8% defect rate"
                  required
                  disabled={isSubmitting}
                />
              </div>

              {/* Recurrence Notes */}
              <div className="form-group">
                <label className="form-label">
                  <span>Recurrence Status</span>
                </label>
                <input
                  type="text"
                  name="recurrence"
                  className="form-input"
                  value={formData.recurrence}
                  onChange={handleChange}
                  placeholder="e.g. No recurrence observed during 14 days"
                  disabled={isSubmitting}
                />
              </div>

              {/* Evidence Quality Grade */}
              <div className="form-group">
                <label className="form-label">
                  <span>Assigned Evidence Grade</span>
                </label>
                <select
                  name="evidence_quality"
                  className="form-select"
                  value={formData.evidence_quality}
                  onChange={handleChange}
                  disabled={isSubmitting}
                >
                  <option value="A">Grade A — Strong (Verified with robust data)</option>
                  <option value="B">Grade B — Moderate (Verified with minor caveats)</option>
                  <option value="C">Grade C — Weak (Inconclusive or contradictory)</option>
                </select>
              </div>
            </div>

            {/* General Notes */}
            <div className="form-group">
              <label className="form-label">
                <span>Verification Notes & Operator Sign-off</span>
              </label>
              <input
                type="text"
                name="notes"
                className="form-input"
                value={formData.notes}
                onChange={handleChange}
                placeholder="e.g. Statistical process control charts verified by Quality Lead."
                disabled={isSubmitting}
              />
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 20 }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-success"
                style={{ minWidth: 180 }}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner" />
                    <span>Retaining in Hindsight...</span>
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    <span>Retain Outcome</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
