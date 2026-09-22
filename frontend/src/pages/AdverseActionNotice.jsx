import { useLocation, useNavigate } from 'react-router-dom';

export default function AdverseActionNotice() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result?.notice) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '80px' }}>
        <p style={{ color: '#9CA3AF', marginBottom: '16px' }}>No notice found. Run an assessment first.</p>
        <button className="btn-primary" onClick={() => navigate('/apply')}>New Application</button>
      </div>
    );
  }

  const { notice, audit_flags } = state.result;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '40px 24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div className="section-label">Regulatory Document</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '28px', fontWeight: 700 }}>Adverse Action Notice</h2>
          <div style={{
            background: audit_flags?.length === 0 ? '#064E3B' : '#450A0A',
            color: audit_flags?.length === 0 ? '#10B981' : '#EF4444',
            padding: '8px 16px', borderRadius: '8px',
            fontSize: '13px', fontWeight: 700,
            border: `1px solid ${audit_flags?.length === 0 ? '#10B981' : '#EF4444'}`,
          }}>
            {audit_flags?.length === 0 ? '✓ AUDIT CLEAN' : `⚠ ${audit_flags.length} FLAGS`}
          </div>
        </div>
        <p style={{ color: '#9CA3AF', fontSize: '14px', marginTop: '4px' }}>
          Generated under ECOA (Regulation B) and FCRA · Applicant: {notice.applicant_id}
        </p>
      </div>

      {/* Disclosure */}
      <div style={{
        background: 'rgba(255,209,0,0.05)',
        border: '1px solid rgba(255,209,0,0.3)',
        borderRadius: '12px', padding: '24px',
        marginBottom: '24px',
      }}>
        <div className="section-label">Disclosure Statement</div>
        <p style={{ color: '#FFFFFF', lineHeight: 1.8, fontSize: '15px' }}>
          {notice.disclosure_statement}
        </p>
      </div>

      {/* Reasons */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="section-label">Specific Reasons for Decision</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {notice.reasons?.map((reason, i) => (
            <div key={i} style={{
              background: '#111111', borderRadius: '10px', padding: '20px',
              borderLeft: '4px solid #FFD100',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                <div>
                  <span style={{ fontSize: '11px', color: '#6B7280', fontWeight: 700, letterSpacing: '0.05em' }}>
                    REASON #{reason.rank}
                  </span>
                  <div style={{ fontSize: '16px', fontWeight: 600, color: '#FFFFFF', marginTop: '4px', lineHeight: 1.4 }}>
                    {reason.plain_english_reason}
                  </div>
                </div>
                <code style={{
                  fontSize: '11px', color: '#FFD100',
                  background: 'rgba(255,209,0,0.1)',
                  padding: '3px 8px', borderRadius: '4px',
                  whiteSpace: 'nowrap', marginLeft: '12px',
                }}>{reason.feature_name}</code>
              </div>
              <div style={{
                background: '#1A1A1A', borderRadius: '8px', padding: '14px',
                borderLeft: '3px solid #3B82F6',
              }}>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#3B82F6', marginBottom: '6px' }}>
                  {reason.regulatory_basis.citation}
                </div>
                <div style={{ fontSize: '13px', color: '#9CA3AF', lineHeight: 1.6 }}>
                  {reason.regulatory_basis.requirement}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px' }}>
        <button className="btn-secondary" onClick={() => navigate(-1)}>← Back</button>
        <button className="btn-secondary" onClick={() => navigate('/apply')}>New Application</button>
      </div>
    </div>
  );
}
