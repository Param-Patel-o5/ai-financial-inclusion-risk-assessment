import { useLocation, useNavigate } from 'react-router-dom';

export default function AdverseActionNotice() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result?.notice) {
    return (
      <div style={{ maxWidth: 1200, margin: '40px auto', padding: '0 24px', textAlign: 'center' }}>
        <p style={{ color: '#9ca3af' }}>No notice found. Please run an assessment first.</p>
        <button className="btn-primary" style={{ marginTop: '16px' }} onClick={() => navigate('/apply')}>
          New Application
        </button>
      </div>
    );
  }

  const { notice, audit_flags } = state.result;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px' }}>
      {/* Header */}
      <div className="card" style={{ marginBottom: '24px', borderColor: '#3b82f6' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div>
            <div style={{ fontSize: '12px', color: '#3b82f6', fontWeight: 600, letterSpacing: '0.1em', marginBottom: '8px' }}>
              ADVERSE ACTION NOTICE — ECOA / REGULATION B / FCRA
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '4px' }}>
              Regulatory Disclosure
            </h2>
            <p style={{ color: '#9ca3af', fontSize: '14px' }}>
              Applicant ID: {notice.applicant_id} · Decision: {notice.decision_band}
            </p>
          </div>
          <div style={{
            background: audit_flags?.length === 0 ? '#064e3b' : '#450a0a',
            color: audit_flags?.length === 0 ? '#10b981' : '#ef4444',
            padding: '8px 16px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 600
          }}>
            {audit_flags?.length === 0 ? '✓ AUDIT CLEAN' : `⚠ ${audit_flags.length} FLAGS`}
          </div>
        </div>
      </div>

      {/* Disclosure Statement */}
      <div className="card" style={{ marginBottom: '24px', background: '#1a2744', borderColor: '#3b82f6' }}>
        <h3 style={{ fontSize: '14px', color: '#3b82f6', fontWeight: 600, marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Disclosure Statement
        </h3>
        <p style={{ color: '#f9fafb', lineHeight: 1.7, fontSize: '15px' }}>
          {notice.disclosure_statement}
        </p>
      </div>

      {/* Reason Codes */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '20px' }}>
          Specific Reasons for Decision
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {notice.reasons?.map((reason, i) => (
            <div key={i} style={{ background: '#1f2937', borderRadius: '10px', padding: '20px', borderLeft: '4px solid #3b82f6' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                <div>
                  <span style={{ fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>REASON #{reason.rank}</span>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: '#f9fafb', marginTop: '4px' }}>
                    {reason.plain_english_reason}
                  </div>
                </div>
                <span style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  background: '#111827',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  whiteSpace: 'nowrap',
                  marginLeft: '12px'
                }}>
                  {reason.feature_name}
                </span>
              </div>
              <div style={{ background: '#111827', borderRadius: '8px', padding: '12px', fontSize: '13px' }}>
                <div style={{ color: '#3b82f6', fontWeight: 600, marginBottom: '4px' }}>
                  {reason.regulatory_basis.citation}
                </div>
                <div style={{ color: '#9ca3af' }}>{reason.regulatory_basis.requirement}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px' }}>
        <button className="btn-secondary" onClick={() => navigate(-1)}>← Back to Result</button>
        <button className="btn-secondary" onClick={() => navigate('/apply')}>New Application</button>
      </div>
    </div>
  );
}
