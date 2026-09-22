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
            <h2 style={{ fontSize: '28px', fontWeight: 800, color: '#FFFFFF' }}>Adverse Action Notice</h2>
            <p style={{ color: '#9CA3AF', fontSize: '14px', marginTop: '4px' }}>
              Statutory Disclosure under ECOA (12 CFR § 1002.9) & FCRA (15 U.S.C. § 1681m) · Applicant: <strong>{notice.applicant_id}</strong>
            </p>
          </div>
          <div style={{
            background: audit_flags?.length === 0 ? '#064E3B' : '#450A0A',
            color: audit_flags?.length === 0 ? '#10B981' : '#EF4444',
            padding: '8px 16px', borderRadius: '8px',
            fontSize: '13px', fontWeight: 700,
            border: `1px solid ${audit_flags?.length === 0 ? '#10B981' : '#EF4444'}`,
          }}>
            {audit_flags?.length === 0 ? '✓ COMPLIANCE AUDIT CLEAN' : `⚠ ${audit_flags.length} FLAGS DETECTED`}
          </div>
        </div>
      </div>

      {/* Dual Lane Explainer Banner */}
      <div style={{
        background: '#111111',
        border: '1px solid #2A2A2A',
        borderRadius: '12px',
        padding: '20px 24px',
        marginBottom: '24px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '24px',
      }}>
        <div style={{ borderRight: '1px solid #2A2A2A', paddingRight: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
            <strong style={{ fontSize: '13px', color: '#10B981', letterSpacing: '0.05em' }}>
              LANE 1: SUBSTANTIVE FACTOR AUTHORIZATION
            </strong>
          </div>
          <p style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.6, margin: 0 }}>
            Grounds each scored model variable in statutory provisions (<strong>12 CFR § 1002.6</strong> & <strong>Form C-1</strong>) authorizing creditors to evaluate income, debt obligations, payment history, and credit experience.
          </p>
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#3B82F6', display: 'inline-block' }} />
            <strong style={{ fontSize: '13px', color: '#3B82F6', letterSpacing: '0.05em' }}>
              LANE 2: PROCEDURAL & AI SPECIFICITY MANDATE
            </strong>
          </div>
          <p style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.6, margin: 0 }}>
            Enforces <strong>12 CFR § 1002.9(b)(2)</strong> and <strong>CFPB Circulars 2022-03 & 2023-03</strong> requiring precise, non-generic plain-English disclosures for AI/ML decisions without black-box vagueness.
          </p>
        </div>
      </div>

      {/* Statutory Disclosure Statement */}
      <div style={{
        background: 'rgba(255,209,0,0.05)',
        border: '1px solid rgba(255,209,0,0.3)',
        borderRadius: '12px', padding: '24px',
        marginBottom: '28px',
      }}>
        <div className="section-label">Statutory Disclosure Statement</div>
        <p style={{ color: '#FFFFFF', lineHeight: 1.8, fontSize: '15px', margin: 0 }}>
          {notice.disclosure_statement}
        </p>
      </div>

      {/* Specific Grounded Reasons */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <div className="section-label">Principal Reasons for Decision (Top Calibrated Model Factors)</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {notice.reasons?.map((reason, i) => {
            const lane1 = reason.lane_1_authorization || reason.regulatory_basis || {};
            const lane2 = reason.lane_2_mandate || {
              citation: '12 CFR § 1002.9(b)(2)',
              requirement: 'The statement of reasons for adverse action must be specific and indicate the principal reasons.',
              clause_id: 'regb_1002_9_b_2',
            };

            return (
              <div key={i} style={{
                background: '#111111', borderRadius: '12px', padding: '22px',
                border: '1px solid #222222',
              }}>
                {/* Header row: Reason rank + Form C-1 category badge + Feature pill */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 800, letterSpacing: '0.05em' }}>
                      REASON #{reason.rank}
                    </span>
                    {reason.standard_category && (
                      <span style={{
                        fontSize: '11px', fontWeight: 700,
                        color: '#FFD100',
                        background: 'rgba(255,209,0,0.1)',
                        border: '1px solid rgba(255,209,0,0.3)',
                        padding: '3px 10px', borderRadius: '6px',
                      }}>
                        Form C-1: {reason.standard_category}
                      </span>
                    )}
                  </div>
                  <code style={{
                    fontSize: '12px', color: '#60A5FA',
                    background: 'rgba(96,165,250,0.1)',
                    border: '1px solid rgba(96,165,250,0.25)',
                    padding: '3px 10px', borderRadius: '6px',
                    whiteSpace: 'nowrap',
                  }}>{reason.feature_name}</code>
                </div>

                {/* Plain English Specific Reason */}
                <div style={{ fontSize: '17px', fontWeight: 600, color: '#FFFFFF', marginBottom: '18px', lineHeight: 1.4 }}>
                  {reason.plain_english_reason}
                </div>

                {/* Dual Lane Cards Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  {/* Lane 1 Box */}
                  <div style={{
                    background: '#161616', borderRadius: '10px', padding: '16px 18px',
                    borderLeft: '3px solid #10B981',
                    border: '1px solid #242424',
                    borderLeftWidth: '3px',
                    borderLeftColor: '#10B981',
                    display: 'flex', flexDirection: 'column', gap: '8px',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '11px', fontWeight: 800, color: '#10B981', letterSpacing: '0.05em' }}>
                        LANE 1 · FACTOR AUTHORIZATION
                      </span>
                      <span style={{ fontSize: '10px', color: '#6B7280', fontFamily: 'monospace' }}>
                        {lane1.clause_id}
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>
                      {lane1.citation}
                    </div>

                    {reason.form_c1_item && (
                      <div style={{
                        fontSize: '11px', color: '#10B981', background: 'rgba(16,185,129,0.08)',
                        border: '1px solid rgba(16,185,129,0.2)', padding: '4px 8px', borderRadius: '4px',
                        fontWeight: 600,
                      }}>
                        📋 {reason.form_c1_item}
                      </div>
                    )}

                    {lane1.statutory_scope && (
                      <div style={{ fontSize: '12px', color: '#D1D5DB', lineHeight: 1.5 }}>
                        <strong>Legal Scope:</strong> {lane1.statutory_scope}
                      </div>
                    )}

                    <div style={{ fontSize: '11px', color: '#9CA3AF', lineHeight: 1.5, fontStyle: 'italic', borderTop: '1px solid #262626', paddingTop: '6px' }}>
                      "{lane1.requirement}"
                    </div>
                  </div>

                  {/* Lane 2 Box */}
                  <div style={{
                    background: '#161616', borderRadius: '10px', padding: '16px 18px',
                    borderLeft: '3px solid #3B82F6',
                    border: '1px solid #242424',
                    borderLeftWidth: '3px',
                    borderLeftColor: '#3B82F6',
                    display: 'flex', flexDirection: 'column', gap: '8px',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '11px', fontWeight: 800, color: '#3B82F6', letterSpacing: '0.05em' }}>
                        LANE 2 · SPECIFICITY & AI MANDATE
                      </span>
                      <span style={{ fontSize: '10px', color: '#6B7280', fontFamily: 'monospace' }}>
                        {lane2.clause_id}
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>
                      {lane2.citation}
                    </div>

                    <div style={{
                      fontSize: '11px', color: '#60A5FA', background: 'rgba(59,130,246,0.08)',
                      border: '1px solid rgba(59,130,246,0.2)', padding: '4px 8px', borderRadius: '4px',
                      fontWeight: 600,
                    }}>
                      ⚖️ AI Governance & Anti-Vagueness Mandate
                    </div>

                    <div style={{ fontSize: '12px', color: '#D1D5DB', lineHeight: 1.5, fontStyle: 'italic', marginTop: '2px' }}>
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
