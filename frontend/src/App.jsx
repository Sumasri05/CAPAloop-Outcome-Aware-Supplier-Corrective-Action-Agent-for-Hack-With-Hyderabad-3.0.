import React, { useState, useEffect } from 'react'
import { Navbar } from './components/Navbar'
import { DashboardView } from './components/DashboardView'
import { DefectForm } from './components/DefectForm'
import { EvidencePanel } from './components/EvidencePanel'
import { RecommendationPanel } from './components/RecommendationPanel'
import { OutcomeModal } from './components/OutcomeModal'
import { TimelineView } from './components/TimelineView'
import { LearningDemoView } from './components/LearningDemoView'
import { api } from './api/client'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [healthStatus, setHealthStatus] = useState('checking')
  const [isSeeding, setIsSeeding] = useState(false)
  
  // Defect Analysis State
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [lastAnalyzedDefect, setLastAnalyzedDefect] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)

  // Outcome Recording State
  const [isOutcomeModalOpen, setIsOutcomeModalOpen] = useState(false)
  const [isSubmittingOutcome, setIsSubmittingOutcome] = useState(false)
  const [outcomeSubmitResult, setOutcomeSubmitResult] = useState(null)

  // Initial health check
  useEffect(() => {
    async function checkBackend() {
      try {
        const res = await api.checkHealth()
        setHealthStatus(res.hindsight || 'unknown')
      } catch {
        setHealthStatus('unreachable')
      }
    }
    checkBackend()
  }, [])

  // Action: Seed experiences
  const handleSeed = async () => {
    setIsSeeding(true)
    setErrorMessage(null)
    try {
      await api.seedExperiences()
    } catch (err) {
      setErrorMessage(`Failed to seed experiences: ${err.message}`)
      throw err
    } finally {
      setIsSeeding(false)
    }
  }

  // Action: Analyze Defect
  const handleAnalyzeDefect = async (defectData) => {
    setIsAnalyzing(true)
    setErrorMessage(null)
    setLastAnalyzedDefect(defectData)
    try {
      const result = await api.analyzeDefect(defectData)
      setAnalysisResult(result)
      setActiveTab('analyze')
    } catch (err) {
      setErrorMessage(`Defect analysis failed: ${err.message}`)
    } finally {
      setIsAnalyzing(false)
    }
  }

  // Action: Submit Outcome
  const handleSubmitOutcome = async (outcomeData) => {
    setIsSubmittingOutcome(true)
    setErrorMessage(null)
    try {
      const res = await api.recordOutcome(outcomeData)
      setOutcomeSubmitResult(res)
    } catch (err) {
      setErrorMessage(`Recording outcome failed: ${err.message}`)
    } finally {
      setIsSubmittingOutcome(false)
    }
  }

  // Action: Test Learning (Re-analyze similar defect after outcome)
  const handleTestLearning = async () => {
    setIsOutcomeModalOpen(false)
    if (lastAnalyzedDefect) {
      await handleAnalyzeDefect(lastAnalyzedDefect)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthStatus={healthStatus}
        onSeed={handleSeed}
        isSeeding={isSeeding}
      />

      <main className="app-container" style={{ flex: 1, width: '100%' }}>
        {/* Global Error Alert */}
        {errorMessage && (
          <div className="alert alert-warning animate-fade-in" style={{ marginBottom: 24 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <div style={{ flex: 1 }}>{errorMessage}</div>
            <button
              onClick={() => setErrorMessage(null)}
              style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Tab 1: Dashboard */}
        {activeTab === 'dashboard' && (
          <DashboardView
            onNavigateAnalyze={() => setActiveTab('analyze')}
            onNavigateDemo={() => setActiveTab('demo')}
            onSeed={handleSeed}
            isSeeding={isSeeding}
            bankId="supplier-quality-capa"
          />
        )}

        {/* Tab 2: Defect Analysis */}
        {activeTab === 'analyze' && (
          <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
            <DefectForm
              onAnalyze={handleAnalyzeDefect}
              isLoading={isAnalyzing}
            />

            {/* Analysis Results View */}
            {analysisResult && (
              <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {/* Result Summary Bar */}
                <div className="glass-panel" style={{
                  padding: '20px 24px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 16,
                  borderLeft: '4px solid var(--cyan-400)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Defect Case ID
                      </div>
                      <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--cyan-400)' }}>
                        {analysisResult.defect_id}
                      </div>
                    </div>

                    <div style={{ height: 32, width: 1, background: 'var(--border-subtle)' }} />

                    <div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                        Target Part & Supplier
                      </div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff' }}>
                        {analysisResult.part_number} • {analysisResult.supplier}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <button
                      className="btn btn-success"
                      onClick={() => {
                        setOutcomeSubmitResult(null)
                        setIsOutcomeModalOpen(true)
                      }}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Record Outcome
                    </button>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setActiveTab('timeline')}
                    >
                      View Timeline
                    </button>
                  </div>
                </div>

                {/* Evidence Panel */}
                <EvidencePanel
                  cases={analysisResult.historical_cases || []}
                  contradictions={analysisResult.recommendation?.contradictory_evidence || []}
                  overallGrade={analysisResult.recommendation?.evidence_grade || 'D'}
                />

                {/* Recommendation Panel */}
                <RecommendationPanel
                  recommendation={analysisResult.recommendation}
                  verificationPlan={analysisResult.verification_plan}
                  onOpenRecordOutcome={() => {
                    setOutcomeSubmitResult(null)
                    setIsOutcomeModalOpen(true)
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Timeline */}
        {activeTab === 'timeline' && (
          <TimelineView selectedDefectId={analysisResult?.defect_id} />
        )}

        {/* Tab 4: Judge Demo */}
        {activeTab === 'demo' && (
          <LearningDemoView />
        )}
      </main>

      {/* Outcome Recording Modal */}
      <OutcomeModal
        isOpen={isOutcomeModalOpen}
        onClose={() => setIsOutcomeModalOpen(false)}
        defectId={analysisResult?.defect_id}
        recommendedAction={analysisResult?.recommendation?.corrective_action}
        onSubmitOutcome={handleSubmitOutcome}
        isSubmitting={isSubmittingOutcome}
        submitResult={outcomeSubmitResult}
        onTestLearning={handleTestLearning}
      />

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '20px 24px',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-dim)',
      }}>
        CAPAloop • Hack With Hyderabad 3.0 • Outcome-Aware Supplier Corrective-Action Decision Support
      </footer>
    </div>
  )
}
