import { useNavigate } from 'react-router-dom';

const REGULATIONS = [
  {
    code: '12 CFR § 1002.6 & § 1002.9',
    lane: 'Lane 1 & Notice Mandate',
    full: 'ECOA / Regulation B',
    desc: 'Statutory authority to evaluate creditworthiness criteria and strict mandate to disclose specific principal reasons for adverse action.',
    url: 'https://www.consumerfinance.gov/rules-policy/regulations/1002/',
  },
  {
    code: '15 U.S.C. § 1681m',
    lane: 'Consumer Reporting Duty',
    full: 'Fair Credit Reporting Act (FCRA)',
    desc: 'Mandates transparent consumer reporting agency disclosure and consumer credit history rights whenever credit reports inform decisions.',
    url: 'https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act',
  },
  {
    code: 'CFPB Circular 2022-03',
    lane: 'Lane 2 AI Governance',
    full: 'Adverse Action & Black-Box AI',
    desc: 'Enforces that algorithmic complexity is no defense: creditors must provide specific, accurate reasons even with advanced ML models.',
    url: 'https://www.consumerfinance.gov/compliance/circulars/circular-2022-03/',
  },
  {
    code: 'CFPB Circular 2023-03',
    lane: 'Lane 2 Reason Specificity',
    full: 'Checklist Form Prohibition',
    desc: 'Prohibits relying on generic sample form checklists if they do not specifically and accurately describe the true AI decision factors.',
    url: 'https://www.consumerfinance.gov/compliance/circulars/circular-2023-03/',
  },
];

export default function Home() {
  const navigate = useNavigate();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 'calc(100vh - 100px)', justifyContent: 'space-between' }}>
      <div className="page-container" style={{ paddingBottom: '32px' }}>
        {/* Hero */}
        <div style={{ textAlign: 'center', padding: '16px 0 20px' }}>
          <h1 style={{
            fontSize: '36px',
            fontWeight: 600,
            lineHeight: 1.25,
            marginBottom: '14px',
            letterSpacing: '-0.3px',
            color: '#FFFFFF',
          }}>
            Every decision, explained.
          </h1>

          <p style={{
            color: '#9CA3AF',
            fontSize: '15px',
            maxWidth: '460px',
            margin: '0 auto 24px',
            lineHeight: 1.5,
          }}>
            AI-powered credit risk assessment for underserved populations with deterministic Dual-Lane regulatory compliance.
          </p>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              style={{
                fontSize: '14px',
                padding: '10px 24px',
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
              onClick={() => navigate('/apply')}
            >
              Assess New Application
            </button>
            <button
              style={{
                fontSize: '14px',
                padding: '10px 20px',
                background: 'transparent',
                color: '#D1D5DB',
                border: '1px solid #4B5563',
                borderRadius: '4px',
                fontWeight: 500,
                cursor: 'pointer',
                fontFamily: 'Inter, sans-serif',
                transition: 'border-color 0.2s, color 0.2s',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = '#9CA3AF';
                e.currentTarget.style.color = '#FFFFFF';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = '#4B5563';
                e.currentTarget.style.color = '#D1D5DB';
              }}
              onClick={() => navigate('/fairness')}
            >
              View Fairness & Compliance Report
            </button>
          </div>
        </div>

        {/* Regulations */}
        <div>
          <div style={{
            fontSize: '12px',
            fontWeight: 600,
            color: '#9CA3AF',
            letterSpacing: '0.04em',
            marginBottom: '12px',
          }}>
            regulatory coverage
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            {REGULATIONS.map(reg => (
              <a key={reg.code} href={reg.url} target="_blank" rel="noreferrer"
                style={{ textDecoration: 'none' }}>
                <div style={{
                  background: '#1C2333',
                  border: '1px solid #2A364F',
                  borderLeft: '2px solid #3B82F6',
                  borderRadius: '4px',
                  padding: '20px',
                  transition: 'border-color 0.2s',
                  cursor: 'pointer',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
                >
                  <div>
                    <div style={{ marginBottom: '8px' }}>
                      <span style={{
                        fontSize: '11px',
                        fontWeight: 500,
                        color: '#6B7280',
                      }}>
                        {reg.lane}
                      </span>
                    </div>
                    <div style={{
                      fontSize: '15px',
                      fontWeight: 700,
                      color: '#FFFFFF',
                      marginBottom: '4px',
                    }}>
                      {reg.code}
                    </div>
                    <div style={{
                      fontSize: '13px',
                      fontWeight: 600,
                      color: '#9CA3AF',
                      marginBottom: '10px',
                    }}>
                      {reg.full}
                    </div>
                    <div style={{ fontSize: '13px', color: '#9CA3AF', lineHeight: 1.5 }}>
                      {reg.desc}
                    </div>
                  </div>
                  <div style={{ marginTop: '16px', fontSize: '12px', color: '#3B82F6', fontWeight: 600 }}>
                    View full statute
                  </div>
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* System Status Strip */}
      <div style={{
        width: '100%',
        background: '#161B22',
        borderTop: '1px solid #21262D',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '32px',
        fontFamily: "'IBM Plex Mono', monospace",
        fontSize: '11px',
        color: '#6B7280',
        whiteSpace: 'nowrap',
        overflowX: 'auto',
      }}>
        <div>
          <span style={{ color: '#9CA3AF' }}>LightGBM</span>{'  '}
          <span style={{ color: '#3FB950' }}>Operational</span>
        </div>

        <span style={{ color: '#374151' }}>|</span>

        <div>
          <span style={{ color: '#9CA3AF' }}>RAG Corpus</span>{'  '}
          <span>4 statutes indexed</span>
        </div>

        <span style={{ color: '#374151' }}>|</span>

        <div>
          <span style={{ color: '#9CA3AF' }}>Last retrain</span>{'  '}
          <span>21 Sept 2026</span>
        </div>

        <span style={{ color: '#374151' }}>|</span>

        <div>
          <span style={{ color: '#9CA3AF' }}>Eval harness</span>{'  '}
          <span>Active</span>
        </div>
      </div>
    </div>
  );
}
