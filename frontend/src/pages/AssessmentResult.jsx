import { useLocation, useNavigate } from 'react-router-dom';

const BAND_CONFIG = {
  Approve: { color: '#10b981', bg: '#064e3b', label: 'APPROVED', icon: '✓' },
  Refer:   { color: '#f59e0b', bg: '#451a03', label: 'REFER FOR REVIEW', icon: '⚠' },
  Deny:    { color: '#ef4444', bg: '#450a0a', label: 'DENIED', icon: '✗' },
};

export default function AssessmentResult() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result) {
    return (
      <div style={{ maxWidth: 1200, margin: '40px auto', padding: '0 24px', textAlign: 'center' }}>
        <p style={{ color: '#9ca3af' }}>No assessment result found.</p>
        <button className="btn-primary" style={{ marginTop: '16px' }} onClick={() => navigate('/apply')}>
          Go to New Application
        </button>
      </div>
    );
  }

  const { result } = state;
  const band = BAND_CONFIG[result.decision_band] || BAND_CONFIG.Refer;

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
      {/* Decision Banner */}
      <div style={{
        background: band.bg,
        border: `2px solid ${band.color}`,
        borderRadius: '16px',
        padding: '32px',
        textAlign: 'center',
        marginBottom: '32px'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '8px' }}>{band.icon}</div>
        <div style={{ fontSize: '32px', fontWeight: 800, color: band.color, marginBottom: '8px' }}>
          {band.label}
        </div>
        <div style={{ color: '#9ca3af', fontSize: '16px' }}>
          Risk Score:{' '}
          <span style={{ color: '#f9fafb', fontWeight: 600 }}>
            {(result.calibrated_probability * 100).toFixed(1)}%
          </span>
          {' '}· Applicant:{' '}
          <span style={{ color: '#f9fafb', fontWeight: 600 }}>{result.applicant_id}</span>
          {result.is_thin_file && (
            <span style={{
              marginLeft: '12px',
              background: '#1e3a5f',
              color: '#3b82f6',
              padding: '2px 10px',
              borderRadius: '12px',
              fontSize: '13px'
            }}>
              Thin-File
            </span>
          )}
        </div>
      </div>

      {/* SHAP Reasons */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px' }}>
          Top Risk Factors
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          {result.shap_features.map((f, i) => (
            <div
              key={i}
              style={{
                background: '#1f2937',
                borderRadius: '10px',
                padding: '16px',
                borderLeft: `4px solid ${f.shap > 0 ? '#ef4444' : '#10b981'}`
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 600, color: '#9ca3af' }}>
                  #{i + 1} {f.feature_name.replace(/_/g, ' ').toUpperCase()}
                </span>
                <span style={{
                  fontSize: '13px',
                  fontWeight: 700,
                  color: f.shap > 0 ? '#ef4444' : '#10b981'
                }}>
                  SHAP: {f.shap > 0 ? '+' : ''}{f.shap.toFixed(3)}
                </span>
              </div>
              <div style={{ fontSize: '14px', color: '#f9fafb' }}>
                Value: <strong>{typeof f.value === 'number' ? f.value.toFixed(2) : f.value}</strong>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Audit Status */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            background: result.audit_flags.length === 0 ? '#064e3b' : '#450a0a',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px'
          }}>
            {result.audit_flags.length === 0 ? '✓' : '⚠'}
          </div>
          <div>
            <div style={{
              fontWeight: 600,
              color: result.audit_flags.length === 0 ? '#10b981' : '#ef4444'
            }}>
              {result.audit_flags.length === 0
                ? 'Compliance Audit: CLEAN'
                : `${result.audit_flags.length} Audit Flag(s) Detected`}
            </div>
            <div style={{ fontSize: '13px', color: '#6b7280' }}>
              Processing time: {result.processing_time_s}s
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          className="btn-primary"
          onClick={() => navigate('/notice', { state })}
        >
          View Adverse Action Notice →
        </button>

        {result.decision_band === 'Refer' && (
          <button
            className="btn-secondary"
            onClick={() => navigate('/underwriter', { state })}
          >
            Submit Underwriter Override
          </button>
        )}

        <button className="btn-secondary" onClick={() => navigate('/apply')}>
          New Application
        </button>
      </div>
    </div>
  );
}
