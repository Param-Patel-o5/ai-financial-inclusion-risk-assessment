import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const REGULATIONS = [
  {
    code: 'ECOA / Reg B',
    full: 'Equal Credit Opportunity Act',
    desc: 'Prohibits discrimination in credit decisions and requires specific adverse action notices.',
    url: 'https://www.consumerfinance.gov/rules-policy/regulations/1002/',
    color: '#FFD100',
  },
  {
    code: 'FCRA',
    full: 'Fair Credit Reporting Act',
    desc: 'Governs use of consumer credit information and requires disclosure when credit reports affect decisions.',
    url: 'https://www.ftc.gov/legal-library/browse/statutes/fair-credit-reporting-act',
    color: '#10B981',
  },
  {
    code: 'CFPB 2022-03',
    full: 'CFPB Circular on Alternative Data',
    desc: 'Guidance on using alternative data sources fairly in credit underwriting for underserved populations.',
    url: 'https://www.consumerfinance.gov/compliance/circulars/circular-2022-03/',
    color: '#3B82F6',
  },
  {
    code: 'CFPB 2023-03',
    full: 'CFPB Circular on AI in Credit',
    desc: 'Requires specific and accurate reasons when AI/ML models are used in adverse action decisions.',
    url: 'https://www.consumerfinance.gov/compliance/circulars/circular-2023-03/',
    color: '#8B5CF6',
  },
];

const FAQS = [
  {
    q: 'What is an Adverse Action Notice?',
    a: 'Under ECOA and FCRA, when a lender denies or takes unfavorable action on a credit application, they must provide specific written reasons. FairTrace generates these automatically using AI with regulatory guardrails.',
  },
  {
    q: 'What is a thin-file applicant?',
    a: 'A thin-file applicant has zero or very few formal credit bureau tradelines. This includes many underbanked individuals who are creditworthy but lack traditional credit history. FairTrace uses alternative data to assess them fairly.',
  },
  {
    q: 'How does FairTrace prevent bias?',
    a: 'Our LightGBM model achieves near-identical AUC scores across thin-file (0.676) and thick-file (0.676) segments. Prohibited demographic terms are blocked at both input and output stages by deterministic guardrails.',
  },
  {
    q: 'What is a SHAP reason code?',
    a: 'SHAP (SHapley Additive exPlanations) values measure how much each feature contributed to the risk score. The top 4 SHAP features become the reason codes in the adverse action notice, grounded in regulatory citations.',
  },
  {
    q: 'Can the system hallucinate regulatory citations?',
    a: 'No. A deterministic post-check verifies every citation against the retrieved regulatory corpus before the notice is returned. Citation hallucination rate across 12 test profiles: 0%.',
  },
];

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      {/* Hero */}
      <div style={{ textAlign: 'center', padding: '60px 0 48px' }}>
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
            ECOA · REG B · FCRA COMPLIANT
          </span>
        </div>

        <h1 style={{
          fontSize: '52px', fontWeight: 800,
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
          maxWidth: '580px', margin: '0 auto 36px',
          lineHeight: 1.7,
        }}>
          AI-powered credit risk assessment designed for underserved populations,
          with full regulatory compliance and zero bias.
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button className="btn-primary"
            style={{ fontSize: '16px', padding: '14px 32px' }}
            onClick={() => navigate('/apply')}>
            Assess New Application →
          </button>
          <button className="btn-secondary"
            style={{ fontSize: '16px', padding: '14px 32px' }}
            onClick={() => navigate('/fairness')}>
            View Fairness Report
          </button>
        </div>
      </div>

      {/* Regulations */}
      <div style={{ marginBottom: '48px' }}>
        <div className="section-label">Regulatory Coverage</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {REGULATIONS.map(reg => (
            <a key={reg.code} href={reg.url} target="_blank" rel="noreferrer"
              style={{ textDecoration: 'none' }}>
              <div className="card" style={{
                borderTop: `3px solid ${reg.color}`,
                transition: 'transform 0.2s, border-color 0.2s',
                cursor: 'pointer', height: '100%',
              }}
                onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div style={{
                  fontSize: '13px', fontWeight: 700,
                  color: reg.color, marginBottom: '6px',
                }}>{reg.code}</div>
                <div style={{
                  fontSize: '14px', fontWeight: 600,
                  color: '#FFFFFF', marginBottom: '8px',
                }}>{reg.full}</div>
                <div style={{ fontSize: '13px', color: '#6B7280', lineHeight: 1.5 }}>
                  {reg.desc}
                </div>
                <div style={{ marginTop: '12px', fontSize: '12px', color: reg.color }}>
                  View Regulation →
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Demo Profiles Quick Start */}
      <div style={{ marginBottom: '48px' }}>
        <div className="section-label">Quick Start — Demo Profiles</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
          {[
            { name: 'Priya Sharma', tag: 'Thin-File · Deny', color: '#EF4444', desc: 'Zero bureau history, high credit-income ratio' },
            { name: 'Marcus Johnson', tag: 'Thick-File · Deny', color: '#EF4444', desc: 'High late payment share, elevated delinquency' },
            { name: 'James Chen', tag: 'Borderline · Refer', color: '#F59E0B', desc: 'Mixed signals, manual review recommended' },
            { name: 'Maria Santos', tag: 'Strong · Approve', color: '#10B981', desc: 'Stable income, clean payment history' },
          ].map(p => (
            <div key={p.name} className="card"
              style={{ cursor: 'pointer', transition: 'border-color 0.2s' }}
              onClick={() => navigate('/apply', { state: { profile: p.name } })}
              onMouseEnter={e => e.currentTarget.style.borderColor = '#FFD100'}
              onMouseLeave={e => e.currentTarget.style.borderColor = '#2A2A2A'}
            >
              <div style={{ fontSize: '15px', fontWeight: 600, marginBottom: '4px' }}>{p.name}</div>
              <div style={{ fontSize: '12px', color: p.color, fontWeight: 600, marginBottom: '8px' }}>{p.tag}</div>
              <div style={{ fontSize: '13px', color: '#6B7280' }}>{p.desc}</div>
            </div>
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
