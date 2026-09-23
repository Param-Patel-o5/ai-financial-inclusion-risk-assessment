import { useLocation, useNavigate } from 'react-router-dom';

export default function AdverseActionNotice() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state?.result?.notice) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '80px' }}>
        <p style={{ color: '#9CA3AF', marginBottom: '16px' }}>No notice found. Run an assessment first.</p>
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
          New Application
        </button>
      </div>
    );
  }

  const { notice, audit_flags } = state.result;

  return (
    <div style={{ maxWidth: 980, margin: '0 auto', padding: '40px 24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{
          fontSize: '12px',
          fontWeight: 600,
          color: '#9CA3AF',
          letterSpacing: '0.02em',
          marginBottom: '6px',
        }}>
          Official Regulatory Notice
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '26px', fontWeight: 700, color: '#FFFFFF', letterSpacing: '-0.3px', margin: 0 }}>
              Adverse Action Notice
            </h2>
            <p style={{ color: '#9CA3AF', fontSize: '13px', marginTop: '4px', margin: 0 }}>
              Applicant ID: <strong style={{ color: '#FFFFFF', fontFamily: "'IBM Plex Mono', monospace" }}>{notice.applicant_id}</strong>
            </p>
          </div>
          <div style={{
            background: 'transparent',
            color: audit_flags?.length === 0 ? '#3FB950' : '#EF4444',
            padding: '4px 10px',
            borderRadius: '3px',
            fontSize: '11px',
            fontWeight: 500,
            border: `1px solid ${audit_flags?.length === 0 ? '#3FB950' : '#EF4444'}`,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontFamily: "'IBM Plex Mono', monospace",
          }}>
            <span style={{
              width: 6, height: 6, borderRadius: '50%',
              background: audit_flags?.length === 0 ? '#3FB950' : '#EF4444',
            }} />
            {audit_flags?.length === 0 ? 'COMPLIANCE AUDIT PASSED' : `${audit_flags.length} AUDIT FLAGS DETECTED`}
          </div>
        </div>
      </div>

      {/* Dual Lane Explainer Banner */}
      <div style={{
        background: '#1C2333',
        border: '1px solid #2A364F',
        borderLeft: '2px solid #3B82F6',
        borderRadius: '4px',
        padding: '18px 22px',
        marginBottom: '24px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '24px',
      }}>
        <div style={{ borderRight: '1px solid #2A364F', paddingRight: '18px' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#8B949E', marginBottom: '6px' }}>
            Lane 1 — Statutory Factor Authorization
          </div>
          <p style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.6, margin: 0 }}>
            Grounds each scored model variable in statutory provisions (<strong>12 CFR § 1002.6</strong> & <strong>Form C-1</strong>) authorizing creditors to evaluate income, debt, and credit history.
          </p>
        </div>
        <div>
          <div style={{ fontSize: '11px', fontWeight: 600, color: '#8B949E', marginBottom: '6px' }}>
            Lane 2 — Procedural & AI Specificity Mandate
          </div>
          <p style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.6, margin: 0 }}>
            Enforces <strong>12 CFR § 1002.9(b)(2)</strong> and <strong>CFPB Circulars 2022-03 & 2023-03</strong> requiring precise, non-generic plain-English disclosures for AI decisions.
          </p>
        </div>
      </div>

      {/* Statutory Disclosure Statement */}
      <div style={{
        background: '#161B22',
        border: '1px solid #21262D',
        borderLeft: '2px solid #3B82F6',
        borderRadius: '4px',
        padding: '20px 24px',
        marginBottom: '28px',
      }}>
        <div style={{
          fontSize: '12px',
          fontWeight: 600,
          color: '#8B949E',
          letterSpacing: '0.02em',
          marginBottom: '8px',
        }}>
          Statutory Disclosure Statement
        </div>
        <p style={{ color: '#CBD5E1', lineHeight: 1.65, fontSize: '14px', margin: 0 }}>
          {notice.disclosure_statement}
        </p>
      </div>

      {/* Specific Grounded Reasons */}
      <div style={{
        background: '#1C2333',
        border: '1px solid #2A364F',
        borderRadius: '4px',
        padding: '24px',
        marginBottom: '28px',
      }}>
        <div style={{
          fontSize: '12px',
          fontWeight: 600,
          color: '#8B949E',
          letterSpacing: '0.02em',
          marginBottom: '20px',
        }}>
          Principal Reasons for Decision
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {notice.reasons?.map((reason, i) => {
            const lane1 = reason.lane_1_authorization || reason.regulatory_basis || {};
            const lane2 = reason.lane_2_mandate || {
              citation: '12 CFR § 1002.9(b)(2)',
              requirement: 'The statement of reasons for adverse action must be specific and indicate the principal reasons.',
            };

            return (
              <div key={i} style={{
                background: '#111111',
                borderRadius: '4px',
                padding: '20px',
                border: '1px solid #222222',
              }}>
                {/* Header row: Reason rank + Feature pill */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ fontSize: '11px', color: '#6B7280', fontWeight: 500 }}>
                    Reason #{reason.rank}
                  </span>
                  <code style={{
                    fontSize: '11px',
                    color: '#8B949E',
                    background: '#1C2333',
                    border: '1px solid #30363D',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontFamily: "'IBM Plex Mono', monospace",
                    whiteSpace: 'nowrap',
                  }}>
                    {reason.feature_name}
                  </code>
                </div>

                {/* Plain English Specific Reason */}
                <div style={{ fontSize: '15px', fontWeight: 600, color: '#FFFFFF', marginBottom: '16px', lineHeight: 1.4 }}>
                  {reason.plain_english_reason}
                </div>

                {/* Dual Lane Cards Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                  {/* Lane 1 Box */}
                  <div style={{
                    background: '#151515',
                    borderRadius: '4px',
                    padding: '14px 16px',
                    border: '1px solid #222222',
                    borderLeft: '2px solid #3B82F6',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px',
                  }}>
                    <div>
                      <span style={{ fontSize: '11px', fontWeight: 500, color: '#6B7280' }}>
                        Lane 1 — Statutory Authority
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF', fontFamily: "'IBM Plex Mono', monospace" }}>
                      {lane1.citation}
                    </div>

                    {(reason.form_c1_item || reason.standard_category) && (
                      <div style={{ fontSize: '12px', lineHeight: 1.4 }}>
                        <span style={{ color: '#8B949E', fontWeight: 500 }}>Checklist: </span>
                        <span style={{ color: '#E6EDF3' }}>{reason.form_c1_item || `Part I: ${reason.standard_category}`}</span>
                      </div>
                    )}

                    {lane1.statutory_scope && (
                      <div style={{ fontSize: '12px', lineHeight: 1.5 }}>
                        <span style={{ color: '#8B949E', fontWeight: 500 }}>Scope: </span>
                        <span style={{ color: '#E6EDF3' }}>{lane1.statutory_scope}</span>
                      </div>
                    )}

                    <div style={{
                      fontSize: '11px',
                      color: '#8B949E',
                      lineHeight: 1.5,
                      fontStyle: 'italic',
                      borderTop: '1px solid #222222',
                      paddingTop: '8px',
                      marginTop: '2px',
                    }}>
                      "{lane1.requirement}"
                    </div>
                  </div>

                  {/* Lane 2 Box */}
                  <div style={{
                    background: '#151515',
                    borderRadius: '4px',
                    padding: '14px 16px',
                    border: '1px solid #222222',
                    borderLeft: '2px solid #3B82F6',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px',
                  }}>
                    <div>
                      <span style={{ fontSize: '11px', fontWeight: 500, color: '#6B7280' }}>
                        Lane 2 — Specificity & AI Mandate
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF', fontFamily: "'IBM Plex Mono', monospace" }}>
                      {lane2.citation}
                    </div>

                    <div style={{
                      fontSize: '11px',
                      color: '#8B949E',
                      lineHeight: 1.5,
                      fontStyle: 'italic',
                      borderTop: '1px solid #222222',
                      paddingTop: '8px',
                      marginTop: '2px',
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
          onClick={() => navigate(-1)}
        >
          Back to Result
        </button>
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
          Assess New Application
        </button>
        <button
          style={{
            fontSize: '14px',
            padding: '10px 18px',
            background: 'transparent',
            color: '#E6EDF3',
            border: '1px solid #30363D',
            borderRadius: '4px',
            fontWeight: 500,
            cursor: 'pointer',
            fontFamily: 'Inter, sans-serif',
          }}
          onClick={() => window.print()}
        >
          Print / Export PDF
        </button>
      </div>
    </div>
  );
}
