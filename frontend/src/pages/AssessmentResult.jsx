import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

const BAND_CONFIG = {
  Approve: { color: '#3FB950', border: '#3FB950', label: 'APPROVED', icon: '✓', sub: 'Application meets credit criteria' },
  Refer: { color: '#F59E0B', border: '#F59E0B', label: 'REFER FOR REVIEW', icon: '⚠', sub: 'Manual underwriter review required' },
  Deny: { color: '#EF4444', border: '#EF4444', label: 'DENIED', icon: '✗', sub: 'Application does not meet credit criteria' },
};

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
        background: '#161B22',
        border: `1px solid ${band.border}`,
        borderRadius: '6px',
        padding: '32px',
        textAlign: 'center',
        marginBottom: '24px',
      }}>
        <div style={{
          width: 52, height: 52, borderRadius: '50%',
          border: `1px solid ${band.border}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '22px', margin: '0 auto 14px',
          color: band.color,
        }}>
          {band.icon}
        </div>
        <div style={{
          fontSize: '28px',
          fontWeight: 700,
          color: band.color,
          fontFamily: "'IBM Plex Mono', monospace",
          marginBottom: '6px',
        }}>
          {band.label}
        </div>
        <div style={{ color: '#9CA3AF', fontSize: '14px', marginBottom: '18px' }}>
          {band.sub}
        </div>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <span style={{
            background: '#111111',
            border: '1px solid #21262D',
            padding: '6px 14px',
            borderRadius: '4px',
            fontSize: '13px',
            color: '#9CA3AF',
          }}>
            Risk Score: <strong style={{ color: '#FFFFFF', fontFamily: "'IBM Plex Mono', monospace" }}>{(result.calibrated_probability * 100).toFixed(1)}%</strong>
          </span>
          <span style={{
            background: '#111111',
            border: '1px solid #21262D',
            padding: '6px 14px',
            borderRadius: '4px',
            fontSize: '13px',
            color: '#9CA3AF',
          }}>
            Applicant: <strong style={{ color: '#FFFFFF', fontFamily: "'IBM Plex Mono', monospace" }}>{result.applicant_id}</strong>
          </span>
          {result.is_thin_file && (
            <span style={{
              border: '1px solid #30363D',
              background: '#1C2333',
              color: '#8B949E',
              padding: '6px 14px',
              borderRadius: '4px',
              fontSize: '11px',
              fontFamily: "'IBM Plex Mono', monospace",
              display: 'flex',
              alignItems: 'center',
            }}>
              Thin-File Applicant
            </span>
          )}
        </div>
      </div>

      {/* SHAP Reasons */}
      <div style={{
        background: '#1C2333',
        border: '1px solid #2A364F',
        borderRadius: '4px',
        padding: '24px',
        marginBottom: '20px',
      }}>
        <div style={{
          fontSize: '12px',
          fontWeight: 600,
          color: '#8B949E',
          letterSpacing: '0.02em',
          marginBottom: '16px',
        }}>
          Top Risk Factors
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
          {result.shap_features.map((f, i) => (
            <div
              key={`${f.feature_name}-${i}`}
              style={{
                background: '#111111',
                borderRadius: '4px',
                padding: '16px',
                border: '1px solid #222222',
                borderLeft: '2px solid #3B82F6',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 500, color: '#6B7280' }}>
                  Factor #{i + 1}
                </span>
                <span style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  color: f.shap > 0 ? '#EF4444' : '#3FB950',
                  fontFamily: "'IBM Plex Mono', monospace",
                }}>
                  {f.shap > 0 ? '▲' : '▼'} {Math.abs(f.shap).toFixed(3)}
                </span>
              </div>
              <div style={{ fontSize: '14px', color: '#E6EDF3', fontWeight: 600, marginBottom: '6px' }}>
                {f.feature_name.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: '13px', color: '#9CA3AF' }}>
                Value: <span style={{ color: '#FFFFFF', fontFamily: "'IBM Plex Mono', monospace" }}>{typeof f.value === 'number' ? f.value.toFixed(3) : f.value}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Audit */}
      <div style={{
        background: '#1C2333',
        border: '1px solid #2A364F',
        borderLeft: '2px solid #3B82F6',
        borderRadius: '4px',
        padding: '16px 20px',
        marginBottom: '24px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: 32, height: 32, borderRadius: '50%',
            border: `1px solid ${result.audit_flags.length === 0 ? '#3FB950' : '#EF4444'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: result.audit_flags.length === 0 ? '#3FB950' : '#EF4444',
            fontSize: '14px', fontWeight: 700,
          }}>
            {result.audit_flags.length === 0 ? '✓' : '!'}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>
              <span style={{ color: '#8B949E' }}>Compliance Audit: </span>
              {result.audit_flags.length === 0 ? (
                <span style={{ color: '#3FB950' }}>CLEAN — No violations detected</span>
              ) : (
                <span style={{ color: '#EF4444' }}>{result.audit_flags.length} Flag(s) Detected</span>
              )}
            </div>
            <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
              Processing time: {result.processing_time_s}s — Model: LightGBM + Isotonic Calibration
            </div>
          </div>
        </div>
        {result.audit_flags.length > 0 && (
          <div style={{ marginTop: '12px' }}>
            {result.audit_flags.map((flag, i) => (
              <div key={i} style={{
                fontSize: '12px', color: '#EF4444',
                fontFamily: "'IBM Plex Mono', monospace", marginTop: '4px',
              }}>
                {flag}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <button
          style={{
            fontSize: '14px',
            padding: '10px 22px',
            background: '#3B82F6',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            cursor: 'pointer',
            fontFamily: 'Inter, sans-serif',
            transition: 'background 0.2s',
          }}
          onMouseEnter={e => e.currentTarget.style.background = '#2563EB'}
          onMouseLeave={e => e.currentTarget.style.background = '#3B82F6'}
          onClick={() => navigate('/notice', { state })}
        >
          View Adverse Action Notice
        </button>
        {result.decision_band === 'Refer' && (
          <button
            style={{
              fontSize: '14px',
              padding: '10px 18px',
              background: 'transparent',
              color: '#FFFFFF',
              border: '1px solid #4B5563',
              borderRadius: '4px',
              fontWeight: 500,
              cursor: 'pointer',
              fontFamily: 'Inter, sans-serif',
            }}
            onClick={() => navigate('/underwriter', { state })}
          >
            Submit Override
          </button>
        )}
        <button
          style={{
            fontSize: '14px',
            padding: '10px 18px',
            background: 'transparent',
            color: '#9CA3AF',
            border: '1px solid #30363D',
            borderRadius: '4px',
            fontWeight: 500,
            cursor: 'pointer',
            fontFamily: 'Inter, sans-serif',
          }}
          onClick={() => navigate('/apply')}
        >
          New Application
        </button>
      </div>

    </div>
  );
}

export default function AssessmentResult() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '80px' }}>
        <p style={{ color: '#9CA3AF', marginBottom: '16px' }}>No assessment result found.</p>
        <button
          style={{
            padding: '10px 20px',
            background: '#3B82F6',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '4px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
          onClick={() => navigate('/apply')}
        >
          Go to New Application
        </button>
      </div>
    );
  }

  const cacheKey = `${state.result.applicant_id}-${state.result.calibrated_probability}`;
  return <ResultView key={cacheKey} result={state.result} />;
}