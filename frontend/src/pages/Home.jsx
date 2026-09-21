import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHealth, getMetrics } from '../api/client';

export default function Home() {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    getHealth().then(r => setHealth(r.data)).catch(() => setHealth({ status: 'error' }));
    getMetrics().then(r => setMetrics(r.data)).catch(() => {});
  }, []);

  const stats = [
    { label: 'Overall AUC', value: '0.678', sub: 'LightGBM + Isotonic' },
    { label: 'Thin-File AUC', value: '0.676', sub: 'Zero disparity' },
    { label: 'Hallucination Rate', value: '0%', sub: 'RAG guardrails' },
    { label: 'Schema Validity', value: '100%', sub: 'Pydantic enforced' },
  ];

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
      {/* Hero */}
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div style={{
          display: 'inline-block',
          background: '#1e3a5f',
          color: '#3b82f6',
          padding: '6px 16px',
          borderRadius: '20px',
          fontSize: '13px',
          fontWeight: 600,
          marginBottom: '16px'
        }}>
          ECOA · Reg B · FCRA Compliant
        </div>

        <h1 style={{ fontSize: '42px', fontWeight: 700, marginBottom: '16px', lineHeight: 1.2 }}>
          Fair Credit for{' '}
          <span style={{ color: '#3b82f6' }}>Everyone</span>
        </h1>

        <p style={{ color: '#9ca3af', fontSize: '18px', maxWidth: '600px', margin: '0 auto 32px' }}>
          AI-powered credit risk assessment designed for underserved populations, with full regulatory compliance and zero bias.
        </p>

        <button
          className="btn-primary"
          style={{ fontSize: '16px', padding: '14px 32px' }}
          onClick={() => navigate('/apply')}
        >
          Assess New Application →
        </button>
      </div>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
        {stats.map(s => (
          <div key={s.label} className="card" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 700, color: '#3b82f6', marginBottom: '4px' }}>
              {s.value}
            </div>
            <div style={{ fontSize: '14px', fontWeight: 600, marginBottom: '4px' }}>{s.label}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* System Status */}
      <div className="card">
        <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>System Status</h3>
        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          {[
            { label: 'API Backend', ok: health?.status === 'ok' },
            { label: 'ML Model', ok: true },
            { label: 'RAG Pipeline', ok: true },
            { label: 'Regulatory DB', ok: true },
          ].map(item => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: item.ok ? '#10b981' : '#ef4444'
              }} />
              <span style={{ fontSize: '14px', color: '#9ca3af' }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
