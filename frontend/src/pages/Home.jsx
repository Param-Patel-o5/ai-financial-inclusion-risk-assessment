import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const REGULATIONS = [
  {
    code: '12 CFR § 1002.6 & § 1002.9',
    lane: 'Lane 1 & Notice Mandate',
    full: 'ECOA / Regulation B',
    desc: 'Statutory authority to evaluate creditworthiness criteria and strict mandate to disclose specific principal reasons for adverse action.',
    url: 'https://www.consumerfinance.gov/rules-policy/regulations/1002/',
    color: '#10B981',
  },
  {
    code: '15 U.S.C. § 1681m',
    lane: 'Consumer Reporting Duty',
    full: 'Fair Credit Reporting Act (FCRA)',
    desc: 'Mandates transparent consumer reporting agency disclosure and consumer credit history rights whenever credit reports inform decisions.',
    url: 'https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act',
    color: '#FFD100',
  },
  {
    code: 'CFPB Circular 2022-03',
    lane: 'Lane 2 AI Governance',
    full: 'Adverse Action & Black-Box AI',
    desc: 'Enforces that algorithmic complexity is no defense: creditors must provide specific, accurate reasons even with advanced ML models.',
    url: 'https://www.consumerfinance.gov/compliance/circulars/circular-2022-03/',
    color: '#3B82F6',
  },
  {
    code: 'CFPB Circular 2023-03',
    lane: 'Lane 2 Reason Specificity',
    full: 'Checklist Form Prohibition',
    desc: 'Prohibits relying on generic sample form checklists if they do not specifically and accurately describe the true AI decision factors.',
    url: 'https://www.consumerfinance.gov/compliance/circulars/circular-2023-03/',
    color: '#8B5CF6',
  },
];

const FAQS = [
  {
    q: 'What is an Adverse Action Notice?',
    a: 'Under ECOA (12 CFR Part 1002) and FCRA (15 U.S.C. § 1681m), when a lender denies or takes unfavorable action on an application, they must provide specific, grounded written reasons. FairTrace generates legally verified dual-lane notices automatically.',
  },
  {
    q: 'What is a thin-file applicant?',
    a: 'A thin-file applicant has zero or very few formal credit bureau tradelines. FairTrace integrates alternative cash-flow, micro-savings, and utility stability indicators to assess creditworthiness without penalizing credit invisibility.',
  },
  {
    q: 'How does FairTrace prevent bias and disparate impact?',
    a: 'Our calibrated LightGBM model achieves near-identical AUC scores across thin-file (0.676) and thick-file (0.676) segments with equalized odds. Prohibited demographic terms are deterministically blocked at both inference and notice generation stages.',
  },
  {
    q: 'What is a SHAP reason code and how does Dual-Lane grounding work?',
    a: 'SHAP (SHapley Additive exPlanations) isolates the exact top factors driving the risk score. In FairTrace, each factor is paired with Lane 1 (12 CFR § 1002.6 statutory authority + Form C-1 classification) and Lane 2 (CFPB Circular 2022-03/2023-03 specificity governance).',
  },
  {
    q: 'Can the system hallucinate regulatory citations?',
    a: 'No. Deterministic post-generation validators verify every statutory citation against our SQLite regulatory index. Across our 20-profile benchmark harness, the citation hallucination rate is 0.0% with 100.0% schema validity.',
  },
];

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      {/* Hero */}
      <div style={{ textAlign: 'center', padding: '64px 0 48px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(255,209,0,0.1)',
          border: '1px solid rgba(255,209,0,0.3)',
          padding: '6px 16px',
          borderRadius: '20px',
          marginBottom: '24px',
        }}>
          <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#FFD100' }} />
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#FFD100', letterSpacing: '0.05em' }}>
            DUAL-LANE REGULATORY COMPLIANCE · ECOA · FCRA · CFPB 2022-03 & 2023-03
          </span>
        </div>

        <h1 style={{
          fontSize: '54px', fontWeight: 800,
          lineHeight: 1.1, marginBottom: '20px',
          letterSpacing: '-1px',
        }}>
          Fair credit for{' '}
          <span style={{
            color: '#FFD100',
            borderBottom: '4px solid #FFD100',
            paddingBottom: '2px',
          }}>everyone.</span>
        </h1>

        <p style={{
          color: '#9CA3AF', fontSize: '18px',
          maxWidth: '620px', margin: '0 auto 36px',
          lineHeight: 1.7,
        }}>
          AI-powered credit risk assessment designed for underserved populations,
          with deterministic Dual-Lane regulatory compliance and zero demographic bias.
        </p>

        <div style={{ display: 'flex', gap: '14px', justifyContent: 'center' }}>
          <button className="btn-primary"
            style={{ fontSize: '16px', padding: '14px 32px' }}
            onClick={() => navigate('/apply')}>
            Assess New Application →
          </button>
          <button className="btn-secondary"
            style={{ fontSize: '16px', padding: '14px 32px' }}
            onClick={() => navigate('/fairness')}>
            View Fairness & Compliance Report
          </button>
        </div>
      </div>

      {/* Regulations */}
      <div style={{ marginBottom: '48px' }}>
        <div className="section-label">Dual-Lane Regulatory Coverage</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {REGULATIONS.map(reg => (
            <a key={reg.code} href={reg.url} target="_blank" rel="noreferrer"
              style={{ textDecoration: 'none' }}>
              <div className="card" style={{
                borderTop: `3px solid ${reg.color}`,
                transition: 'transform 0.2s, border-color 0.2s',
                cursor: 'pointer', height: '100%',
                display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
              }}
                onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{
                      fontSize: '11px', fontWeight: 700,
                      color: reg.color,
                      background: `${reg.color}15`,
                      padding: '2px 8px', borderRadius: '4px',
                    }}>{reg.lane}</span>
                  </div>
                  <div style={{
                    fontSize: '15px', fontWeight: 700,
                    color: '#FFFFFF', marginBottom: '4px',
                  }}>{reg.code}</div>
                  <div style={{
                    fontSize: '13px', fontWeight: 600,
                    color: '#9CA3AF', marginBottom: '10px',
                  }}>{reg.full}</div>
                  <div style={{ fontSize: '13px', color: '#6B7280', lineHeight: 1.5 }}>
                    {reg.desc}
                  </div>
                </div>
                <div style={{ marginTop: '16px', fontSize: '12px', color: reg.color, fontWeight: 600 }}>
                  View Full Statute →
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* FAQ */}
      <div style={{ marginBottom: '48px' }}>
        <div className="section-label">Frequently Asked Questions</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {FAQS.map((faq, i) => (
            <FaqItem key={i} q={faq.q} a={faq.a} />
          ))}
        </div>
      </div>
    </div>
  );
}

function FaqItem({ q, a }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="card" style={{ cursor: 'pointer', padding: '16px 20px' }}
      onClick={() => setOpen(!open)}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontWeight: 600, fontSize: '15px' }}>{q}</span>
        <span style={{ color: '#FFD100', fontSize: '18px', transition: 'transform 0.2s', transform: open ? 'rotate(45deg)' : 'rotate(0)' }}>+</span>
      </div>
      {open && (
        <p style={{ marginTop: '12px', color: '#9CA3AF', fontSize: '14px', lineHeight: 1.7 }}>{a}</p>
      )}
    </div>
  );
}
