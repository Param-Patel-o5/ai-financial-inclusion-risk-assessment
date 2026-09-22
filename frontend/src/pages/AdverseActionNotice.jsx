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
    <div style={{ maxWidth: 980, margin: '0 auto', padding: '40px 24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div className="section-label">Official Regulatory Notice</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '28px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.5px' }}>Adverse Action Notice</h2>
            <p style={{ color: '#9CA3AF', fontSize: '14px', marginTop: '4px' }}>
              Applicant ID: <strong style={{ color: '#FFFFFF' }}>{notice.applicant_id}</strong>
            </p>
          </div>
          <div style={{
            background: audit_flags?.length === 0 ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
            color: audit_flags?.length === 0 ? '#10B981' : '#EF4444',
            padding: '8px 16px', borderRadius: '8px',
            fontSize: '12px', fontWeight: 700,
            border: `1px solid ${audit_flags?.length === 0 ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
            display: 'inline-flex', alignItems: 'center', gap: '8px', letterSpacing: '0.04em',
          }}>
            <span style={{
              width: 6, height: 6, borderRadius: '50%',
              background: audit_flags?.length === 0 ? '#10B981' : '#EF4444',
            }} />
            {audit_flags?.length === 0 ? 'COMPLIANCE AUDIT PASSED' : `${audit_flags.length} AUDIT FLAGS DETECTED`}
          </div>
        </div>
      </div>

      {/* Dual Lane Explainer Banner */}
      <div style={{
        background: '#111111',
        border: '1px solid #242424',
        borderRadius: '12px',
        padding: '18px 22px',
        marginBottom: '24px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '24px',
      }}>
        <div style={{ borderRight: '1px solid #222222', paddingRight: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#10B981', letterSpacing: '0.05em' }}>
              LANE 1: STATUTORY FACTOR AUTHORIZATION
            </span>
          </div>
          <p style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.6, margin: 0 }}>
            Grounds each scored model variable in statutory provisions (<strong>12 CFR § 1002.6</strong> & <strong>Form C-1</strong>) authorizing creditors to evaluate income, debt, and credit history.
          </p>
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#3B82F6' }} />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#3B82F6', letterSpacing: '0.05em' }}>
              LANE 2: PROCEDURAL & AI SPECIFICITY MANDATE
            </span>
          </div>
          <p style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.6, margin: 0 }}>
            Enforces <strong>12 CFR § 1002.9(b)(2)</strong> and <strong>CFPB Circulars 2022-03 & 2023-03</strong> requiring precise, non-generic plain-English disclosures for AI decisions.
          </p>
        </div>
      </div>

      {/* Statutory Disclosure Statement */}
      <div style={{
        background: 'rgba(255,209,0,0.03)',
        border: '1px solid rgba(255,209,0,0.25)',
        borderRadius: '12px', padding: '20px 24px',
        marginBottom: '28px',
      }}>
        <div className="section-label" style={{ marginBottom: '8px' }}>Statutory Disclosure Statement</div>
        <p style={{ color: '#E5E7EB', lineHeight: 1.7, fontSize: '14px', margin: 0 }}>
          {notice.disclosure_statement}
        </p>
      </div>

      {/* Specific Grounded Reasons */}
      <div className="card" style={{ marginBottom: '28px', padding: '24px' }}>
        <div className="section-label">Principal Reasons for Decision</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {notice.reasons?.map((reason, i) => {
            const lane1 = reason.lane_1_authorization || reason.regulatory_basis || {};
            const lane2 = reason.lane_2_mandate || {
              citation: '12 CFR § 1002.9(b)(2)',
              requirement: 'The statement of reasons for adverse action must be specific and indicate the principal reasons.',
            };

            return (
              <div key={i} style={{
                background: '#111111', borderRadius: '10px', padding: '20px',
                border: '1px solid #222222',
              }}>
                {/* Header row: Reason rank + Feature pill */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ fontSize: '12px', color: '#9CA3AF', fontWeight: 800, letterSpacing: '0.05em' }}>
                    REASON #{reason.rank}
                  </span>
                  <code style={{
                    fontSize: '11px', color: '#60A5FA',
                    background: 'rgba(96,165,250,0.08)',
                    border: '1px solid rgba(96,165,250,0.2)',
                    padding: '3px 10px', borderRadius: '6px',
                    whiteSpace: 'nowrap',
                  }}>{reason.feature_name}</code>
                </div>

                {/* Plain English Specific Reason */}
                <div style={{ fontSize: '16px', fontWeight: 600, color: '#FFFFFF', marginBottom: '16px', lineHeight: 1.4 }}>
                  {reason.plain_english_reason}
                </div>

                {/* Dual Lane Cards Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                  {/* Lane 1 Box */}
                  <div style={{
                    background: '#151515', borderRadius: '8px', padding: '14px 16px',
                    border: '1px solid #222222',
                    borderLeft: '3px solid #10B981',
                    display: 'flex', flexDirection: 'column', gap: '8px',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '10px', fontWeight: 800, color: '#10B981', letterSpacing: '0.05em' }}>
                        LANE 1 · STATUTORY AUTHORITY
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>
                      {lane1.citation}
                    </div>

                    {(reason.form_c1_item || reason.standard_category) && (
                      <div style={{ fontSize: '12px', color: '#FFD100', lineHeight: 1.4 }}>
                        <span style={{ color: '#9CA3AF', fontWeight: 600 }}>Checklist: </span>
                        {reason.form_c1_item || `Part I: ${reason.standard_category}`}
                      </div>
                    )}

                    {lane1.statutory_scope && (
                      <div style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.5 }}>
                        <span style={{ color: '#D1D5DB', fontWeight: 600 }}>Scope: </span>
                        {lane1.statutory_scope}
                      </div>
                    )}

                    <div style={{
                      fontSize: '11px', color: '#9CA3AF', lineHeight: 1.5,
                      fontStyle: 'italic', borderTop: '1px solid #222222', paddingTop: '8px', marginTop: '2px',
                    }}>
                      "{lane1.requirement}"
                    </div>
                  </div>

                  {/* Lane 2 Box */}
                  <div style={{
                    background: '#151515', borderRadius: '8px', padding: '14px 16px',
                    border: '1px solid #222222',
                    borderLeft: '3px solid #3B82F6',
                    display: 'flex', flexDirection: 'column', gap: '8px',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '10px', fontWeight: 800, color: '#3B82F6', letterSpacing: '0.05em' }}>
                        LANE 2 · SPECIFICITY & AI MANDATE
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>
                      {lane2.citation}
                    </div>

                    <div style={{
                      fontSize: '11px', color: '#9CA3AF', lineHeight: 1.5,
                      fontStyle: 'italic', borderTop: '1px solid #222222', paddingTop: '8px', marginTop: '2px',
                    }}>
                      "{lane2.requirement}"
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <button className="btn-secondary" onClick={() => navigate(-1)}>← Back to Result</button>
        <button className="btn-secondary" onClick={() => navigate('/apply')}>Assess New Application</button>
        <button className="btn-ghost" onClick={() => window.print()}>Print / Export PDF</button>
      </div>
    </div>
  );
}
