import React, { useState } from 'react'

const PRESETS = [
  {
    name: 'Apex: Surface Cracks',
    badge: 'Standard Case',
    data: {
      supplier: 'Apex Components',
      part_number: 'BRK-204',
      defect_type: 'Surface cracks',
      severity: 'major',
      manufacturing_process: 'Metal stamping',
      description: 'Fine surface cracks appearing near stamped bend radius following die change.',
      root_cause_hypothesis: 'Excessive forming pressure or worn punch radius.',
    },
  },
  {
    name: 'Titan: Flange Porosity',
    badge: 'Contradictory Case',
    data: {
      supplier: 'Titan Castings',
      part_number: 'CAS-102',
      defect_type: 'Flange porosity',
      severity: 'critical',
      manufacturing_process: 'High pressure die casting',
      description: 'Subsurface gas porosity revealed during face milling operation on mounting flange.',
      root_cause_hypothesis: 'Insufficient vacuum venting or turbulent metal injection flow.',
    },
  },
  {
    name: 'Nova: Solder Voids',
    badge: 'New Defect',
    data: {
      supplier: 'Nova Electronics',
      part_number: 'PCB-990',
      defect_type: 'Solder joint voiding',
      severity: 'minor',
      manufacturing_process: 'Surface mount technology (SMT)',
      description: 'BGA solder voiding rate exceeding 25% area requirement on thermal ground pad.',
      root_cause_hypothesis: 'Sub-optimal reflow thermal soak profile or paste outgassing.',
    },
  },
]

export function DefectForm({ onAnalyze, isLoading }) {
  const [formData, setFormData] = useState({
    supplier: 'Apex Components',
    part_number: 'BRK-204',
    defect_type: 'Surface cracks',
    severity: 'major',
    manufacturing_process: 'Metal stamping',
    description: 'Fine surface cracks appearing near stamped bend radius following die change.',
    root_cause_hypothesis: 'Excessive forming pressure or worn punch radius.',
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleApplyPreset = (preset) => {
    setFormData(preset.data)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onAnalyze(formData)
  }

  return (
    <div className="glass-panel" style={{ padding: 28 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>
            New Defect Submission
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Enter supplier quality observations to query Hindsight memory and generate recommendations.
          </p>
        </div>

        {/* Quick Presets */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Quick Demo Presets:</span>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleApplyPreset(p)}
              disabled={isLoading}
              style={{ fontSize: '0.78rem', padding: '4px 10px' }}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: 16,
          marginBottom: 12,
        }}>
          {/* Supplier */}
          <div className="form-group">
            <label className="form-label">
              <span>Supplier Name *</span>
            </label>
            <input
              type="text"
              name="supplier"
              className="form-input"
              value={formData.supplier}
              onChange={handleChange}
              placeholder="e.g. Apex Components"
              required
              disabled={isLoading}
            />
          </div>

          {/* Part Number */}
          <div className="form-group">
            <label className="form-label">
              <span>Part Number *</span>
            </label>
            <input
              type="text"
              name="part_number"
              className="form-input"
              value={formData.part_number}
              onChange={handleChange}
              placeholder="e.g. BRK-204"
              required
              disabled={isLoading}
            />
          </div>

          {/* Defect Type */}
          <div className="form-group">
            <label className="form-label">
              <span>Defect Type *</span>
            </label>
            <input
              type="text"
              name="defect_type"
              className="form-input"
              value={formData.defect_type}
              onChange={handleChange}
              placeholder="e.g. Surface cracks"
              required
              disabled={isLoading}
            />
          </div>

          {/* Severity */}
          <div className="form-group">
            <label className="form-label">
              <span>Severity *</span>
            </label>
            <select
              name="severity"
              className="form-select"
              value={formData.severity}
              onChange={handleChange}
              required
              disabled={isLoading}
            >
              <option value="critical">Critical</option>
              <option value="major">Major</option>
              <option value="minor">Minor</option>
              <option value="cosmetic">Cosmetic</option>
            </select>
          </div>

          {/* Manufacturing Process */}
          <div className="form-group" style={{ gridColumn: 'span 2' }}>
            <label className="form-label">
              <span>Manufacturing Process *</span>
            </label>
            <input
              type="text"
              name="manufacturing_process"
              className="form-input"
              value={formData.manufacturing_process}
              onChange={handleChange}
              placeholder="e.g. Metal stamping, High pressure die casting, SMT reflow"
              required
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Description */}
        <div className="form-group">
          <label className="form-label">
            <span>Defect Description & Context *</span>
          </label>
          <textarea
            name="description"
            className="form-textarea"
            rows="3"
            value={formData.description}
            onChange={handleChange}
            placeholder="Detailed description of defect observations, inspection lot, tooling changes..."
            required
            disabled={isLoading}
          />
        </div>

        {/* Root Cause Hypothesis */}
        <div className="form-group">
          <label className="form-label">
            <span>Root-Cause Hypothesis (Optional)</span>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Helps refine Hindsight recall</span>
          </label>
          <input
            type="text"
            name="root_cause_hypothesis"
            className="form-input"
            value={formData.root_cause_hypothesis}
            onChange={handleChange}
            placeholder="e.g. Excessive forming pressure, improper cooling rate"
            disabled={isLoading}
          />
        </div>

        {/* Submit */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
          <button
            type="submit"
            className="btn btn-primary"
            style={{ minWidth: 200, padding: '12px 24px' }}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner" />
                <span>Querying Hindsight...</span>
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <span>Analyze Defect</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
