/**
 * CAPAloop API Client.
 *
 * Centralizes all communication with the FastAPI backend.
 * Uses relative URLs to work seamlessly with Vite proxy or production hosting.
 */

const API_BASE = ''

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`
    try {
      const errJson = await response.json()
      if (errJson && errJson.detail) {
        errorDetail = errJson.detail
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail)
  }
  return response.json()
}

export const api = {
  /** Check backend health and Hindsight status */
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`)
    return handleResponse(res)
  },

  /** Seed 10 synthetic supplier-quality experiences */
  async seedExperiences() {
    const res = await fetch(`${API_BASE}/api/v1/seed`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    return handleResponse(res)
  },

  /**
   * Analyze a supplier defect.
   * Calls POST /api/v1/defects/analyze
   */
  async analyzeDefect(defect) {
    const res = await fetch(`${API_BASE}/api/v1/defects/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(defect),
    })
    return handleResponse(res)
  },

  /**
   * Record a verified outcome and retain into Hindsight.
   * Calls POST /api/v1/defects/outcome
   */
  async recordOutcome(outcomeData) {
    const res = await fetch(`${API_BASE}/api/v1/defects/outcome`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(outcomeData),
    })
    return handleResponse(res)
  },

  /**
   * Fetch timeline events for a defect.
   * Calls GET /api/v1/defects/{defect_id}/timeline
   */
  async getTimeline(defectId) {
    const url = defectId
      ? `${API_BASE}/api/v1/defects/${encodeURIComponent(defectId)}/timeline`
      : `${API_BASE}/api/learning/timeline`
    const res = await fetch(url)
    return handleResponse(res)
  },
}
