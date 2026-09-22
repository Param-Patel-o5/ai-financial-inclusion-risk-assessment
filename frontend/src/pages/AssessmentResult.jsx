import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

const BAND_CONFIG = {
  Approve: { color: '#10B981', bg: '#064E3B', border: '#10B981', label: 'APPROVED', icon: '✓', sub: 'Application meets credit criteria' },
  Refer: { color: '#F59E0B', bg: '#451A03', border: '#F59E0B', label: 'REFER FOR REVIEW', icon: '⚠', sub: 'Manual underwriter review required' },
  Deny: { color: '#EF4444', bg: '#450A0A', border: '#EF4444', label: 'DENIED', icon: '✗', sub: 'Application does not meet credit criteria' },
};

// ── Inner component — gets a fresh key from wrapper on every new result ──
function ResultView({ result }) {
  const navigate = useNavigate();
  const band = BAND_CONFIG[result.decision_band] || BAND_CONFIG.Refer;
  const state = { result };

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="page-container">

      {/* Decision Banner */}
      <div style={{
        background: band.bg,
        border: `2px solid ${band.border}`,
        borderRadius: '16px', padding: '36px',
        textAlign: 'center', marginBottom: '28px',
      }}>
        <div style={{
          width: 64, height: 64, borderRadius: '50%',
          background: `${band.color}20`,
          border: `2px solid ${band.color}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '28px', margin: '0 auto 16px',
          color: band.color,
        }}>
          {band.icon}
        </div>
        <div style={{ fontSize: '36px', fontWeight: 800, color: band.color, marginBottom: '6px' }}>
          {band.label}
        </div>
        <div style={{ color: '#9CA3AF', fontSize: '15px', marginBottom: '16px' }}>
          {band.sub}
        </div>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <span style={{ background: '#111111', padding: '6px 16px', borderRadius: '8px', fontSize: '14px' }}>
            Risk Score: <strong style={{ color: '#FFFFFF' }}>{(result.calibrated_probability * 100).toFixed(1)}%</strong>
          </span>
          <span style={{ background: '#111111', padding: '6px 16px', borderRadius: '8px', fontSize: '14px' }}>
            Applicant: <strong style={{ color: '#FFFFFF' }}>{result.applicant_id}</strong>
          </span>
          {result.is_thin_file && (
            <span style={{
              background: 'rgba(255,209,0,0.1)', border: '1px solid #FFD100',
              color: '#FFD100', padding: '6px 16px', borderRadius: '8px',
              fontSize: '13px', fontWeight: 600,
            }}>
              Thin-File Applicant
            </span>
          )}
        </div>
      </div>

      {/* SHAP Reasons */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="section-label">Top Risk Factors</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
          {result.shap_features.map((f, i) => (
            <div
              key={`${f.feature_name}-${i}`}
              style={{
                background: '#111111', borderRadius: '10px', padding: '16px',
                borderLeft: `4px solid ${f.shap > 0 ? '#EF4444' : '#10B981'}`,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#9CA3AF' }}>
                  FACTOR #{i + 1}
                </span>
                <span style={{ fontSize: '13px', fontWeight: 700, color: f.shap > 0 ? '#EF4444' : '#10B981' }}>
                  {f.shap > 0 ? '▲' : '▼'} {Math.abs(f.shap).toFixed(3)}
                </span>
              </div>
              <div style={{ fontSize: '13px', color: '#FFD100', fontWeight: 600, marginBottom: '4px' }}>
                {f.feature_name.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: '14px', color: '#FFFFFF' }}>
                Value: <strong>{typeof f.value === 'number' ? f.value.toFixed(3) : f.value}</strong>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Audit */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: 36, height: 36, borderRadius: '50%',
            background: result.audit_flags.length === 0 ? '#064E3B' : '#450A0A',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: result.audit_flags.length === 0 ? '#10B981' : '#EF4444',
            fontSize: '16px', fontWeight: 700,
          }}>
            {result.audit_flags.length === 0 ? '✓' : '!'}
          </div>
          <div>
            <div style={{
              fontWeight: 600, fontSize: '15px',
              color: result.audit_flags.length === 0 ? '#10B981' : '#EF4444',
            }}>
              {result.audit_flags.length === 0
                ? 'Compliance Audit: CLEAN — No violations detected'
                : `${result.audit_flags.length} Compliance Flag(s) Detected`}
            </div>
            <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
              Processing time: {result.processing_time_s}s · Model: LightGBM + Isotonic Calibration
            </div>
          </div>
        </div>
        {result.audit_flags.length > 0 && (
          <div style={{ marginTop: '12px' }}>
            {result.audit_flags.map((flag, i) => (
              <div key={i} style={{
                fontSize: '12px', color: '#EF4444',
                fontFamily: 'monospace', marginTop: '4px',
              }}>
                {flag}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <button className="btn-primary" onClick={() => navigate('/notice', { state })}>
          View Adverse Action Notice →
        </button>
        {result.decision_band === 'Refer' && (
          <button className="btn-ghost" onClick={() => navigate('/underwriter', { state })}>
            Submit Override
          </button>
        )}
        <button className="btn-secondary" onClick={() => navigate('/apply')}>
          New Application
        </button>
      </div>

    </div>
  );
}

// ── Wrapper — key forces full remount on every new result ──
export default function AssessmentResult() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '80px' }}>
        <p style={{ color: '#9CA3AF', marginBottom: '16px' }}>No assessment result found.</p>
        <button className="btn-primary" onClick={() => navigate('/apply')}>
          Go to New Application
        </button>
      </div>
    );
  }

  const cacheKey = `${state.result.applicant_id}-${state.result.calibrated_probability}`;

  return <ResultView key={cacheKey} result={state.result} />;
}