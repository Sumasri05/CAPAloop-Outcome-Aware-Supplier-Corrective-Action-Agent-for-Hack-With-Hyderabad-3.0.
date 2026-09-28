import React, { useState } from 'react'

export function Navbar({ activeTab, setActiveTab, healthStatus, onSeed, isSeeding }) {
  const [seedSuccess, setSeedSuccess] = useState(false)

  const handleSeedClick = async () => {
    try {
      await onSeed()
      setSeedSuccess(true)
      setTimeout(() => setSeedSuccess(false), 3000)
    } catch {
      // error handled in parent
    }
  }

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(10, 13, 20, 0.85)',
      backdropFilter: 'blur(12px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '14px 24px',
    }}>
      <div style={{
        maxWidth: 1320,
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16,
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: 12,
            background: 'linear-gradient(135deg, var(--cyan-500), var(--indigo-600))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)',
          }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
            </svg>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="brand-font" style={{ fontSize: '1.35rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.03em' }}>
                CAPA<span style={{ color: 'var(--cyan-400)' }}>loop</span>
              </span>
              <span className="badge badge-grade-b" style={{ fontSize: '0.68rem', padding: '2px 7px' }}>
                Outcome-Aware
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Supplier Corrective-Action Decision Agent
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          background: 'rgba(19, 28, 46, 0.6)',
          padding: 4,
          borderRadius: 'var(--radius-full)',
          border: '1px solid var(--border-subtle)',
        }}>
          <button
            className={`tab-pill ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`tab-pill ${activeTab === 'analyze' ? 'active' : ''}`}
            onClick={() => setActiveTab('analyze')}
          >
            Defect Analysis
          </button>
          <button
            className={`tab-pill ${activeTab === 'timeline' ? 'active' : ''}`}
            onClick={() => setActiveTab('timeline')}
          >
            Live Timeline
          </button>
          <button
            className={`tab-pill ${activeTab === 'demo' ? 'active' : ''}`}
            onClick={() => setActiveTab('demo')}
            style={{
              color: activeTab === 'demo' ? '#c084fc' : undefined,
              borderColor: activeTab === 'demo' ? 'rgba(168, 85, 247, 0.4)' : undefined,
            }}
          >
            ★ Judge Demo
          </button>
        </nav>

        {/* Status & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Hindsight Status Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 7,
            background: 'rgba(15, 23, 42, 0.8)',
            padding: '6px 12px',
            borderRadius: 'var(--radius-full)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.78rem',
            color: 'var(--text-muted)',
          }}>
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: healthStatus === 'connected' ? 'var(--emerald-400)' : 'var(--amber-400)',
              boxShadow: healthStatus === 'connected' ? '0 0 8px var(--emerald-400)' : '0 0 8px var(--amber-400)',
              display: 'inline-block',
            }} />
            <span>Hindsight: <strong style={{ color: '#fff' }}>{healthStatus || 'checking...'}</strong></span>
          </div>

          {/* Seed Button */}
          <button
            className="btn btn-secondary btn-sm"
            onClick={handleSeedClick}
            disabled={isSeeding}
            title="Seed Hindsight Cloud bank with 10 synthetic supplier quality experiences"
          >
            {isSeeding ? (
              <>
                <span className="spinner" style={{ width: 12, height: 12 }} />
                <span>Seeding...</span>
              </>
            ) : seedSuccess ? (
              <>
                <span style={{ color: 'var(--emerald-400)' }}>✓</span>
                <span>Seeded 10 Cases</span>
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
                <span>Seed Knowledge</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}
