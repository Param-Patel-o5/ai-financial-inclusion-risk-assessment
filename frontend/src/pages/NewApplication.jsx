import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { assessApplicant } from '../api/client';

const DEMO_PROFILES = {
  priya: {
    applicant_id: 'PRIYA_001',
    label: 'Priya Sharma',
    tag: 'Thin-File · Likely Deny',
    tagColor: '#ef4444',
    AMT_INCOME_TOTAL: 85000,
    AMT_CREDIT: 520000,
    AMT_ANNUITY: 26000,
    credit_income_ratio: 6.12,
    annuity_income_ratio: 0.31,
    employment_years: 0.8,
    late_payment_share: 0.05,
    mean_days_late: 2.0,
    max_days_late: 5.0,
    underpayment_share: 0.04,
    installments_count: 3.0,
    prev_applications_count: 2.0,
    prev_refused_count: 1.0,
    prev_refusal_rate: 0.50,
    thin_file: 1.0,
    bureau_active_credits_count: 0.0,
  },
  marcus: {
    applicant_id: 'MARCUS_002',
    label: 'Marcus Johnson',
    tag: 'Thick-File · Likely Deny',
    tagColor: '#ef4444',
    AMT_INCOME_TOTAL: 120000,
    AMT_CREDIT: 680000,
    AMT_ANNUITY: 34000,
    credit_income_ratio: 5.67,
    annuity_income_ratio: 0.28,
    employment_years: 2.1,
    late_payment_share: 0.44,
    mean_days_late: 19.0,
    max_days_late: 48.0,
    underpayment_share: 0.32,
    installments_count: 9.0,
    prev_applications_count: 5.0,
    prev_refused_count: 3.0,
    prev_refusal_rate: 0.60,
    thin_file: 0.0,
    bureau_active_credits_count: 2.0,
  },
  james: {
    applicant_id: 'JAMES_003',
    label: 'James Chen',
    tag: 'Borderline · Likely Refer',
    tagColor: '#f59e0b',
    AMT_INCOME_TOTAL: 150000,
    AMT_CREDIT: 420000,
    AMT_ANNUITY: 21000,
    credit_income_ratio: 2.80,
    annuity_income_ratio: 0.14,
    employment_years: 3.5,
    late_payment_share: 0.18,
    mean_days_late: 8.0,
    max_days_late: 22.0,
    underpayment_share: 0.12,
    installments_count: 11.0,
    prev_applications_count: 3.0,
    prev_refused_count: 1.0,
    prev_refusal_rate: 0.33,
    thin_file: 0.0,
    bureau_active_credits_count: 3.0,
  },
  maria: {
    applicant_id: 'MARIA_004',
    label: 'Maria Santos',
    tag: 'Strong Profile · Likely Approve',
    tagColor: '#10b981',
    AMT_INCOME_TOTAL: 220000,
    AMT_CREDIT: 280000,
    AMT_ANNUITY: 14000,
    credit_income_ratio: 1.27,
    annuity_income_ratio: 0.06,
    employment_years: 7.2,
    late_payment_share: 0.03,
    mean_days_late: 1.0,
    max_days_late: 3.0,
    underpayment_share: 0.02,
    installments_count: 18.0,
    prev_applications_count: 4.0,
    prev_refused_count: 0.0,
    prev_refusal_rate: 0.0,
    thin_file: 0.0,
    bureau_active_credits_count: 5.0,
  },
};

const FIELDS = [
  {
    group: 'Loan Details',
    fields: [
      { key: 'AMT_INCOME_TOTAL', label: 'Annual Income (₹)' },
      { key: 'AMT_CREDIT', label: 'Credit Amount (₹)' },
      { key: 'AMT_ANNUITY', label: 'Annual Annuity (₹)' },
      { key: 'credit_income_ratio', label: 'Credit / Income Ratio' },
      { key: 'annuity_income_ratio', label: 'Annuity / Income Ratio' },
    ]
  },
  {
    group: 'Employment',
    fields: [
      { key: 'employment_years', label: 'Employment Years' },
    ]
  },
  {
    group: 'Payment History',
    fields: [
      { key: 'late_payment_share', label: 'Late Payment Share (0-1)' },
      { key: 'mean_days_late', label: 'Mean Days Late' },
      { key: 'max_days_late', label: 'Max Days Late' },
      { key: 'underpayment_share', label: 'Underpayment Share (0-1)' },
      { key: 'installments_count', label: 'Installments Count' },
    ]
  },
  {
    group: 'Credit Profile',
    fields: [
      { key: 'prev_applications_count', label: 'Previous Applications' },
      { key: 'prev_refused_count', label: 'Previous Refusals' },
      { key: 'prev_refusal_rate', label: 'Refusal Rate (0-1)' },
      { key: 'thin_file', label: 'Thin File (0 or 1)' },
      { key: 'bureau_active_credits_count', label: 'Active Credits Count' },
    ]
  },
];

export default function NewApplication() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    applicant_id: 'APPLICANT_001',
    ...DEMO_PROFILES.james
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadProfile = (key) => {
    setForm({ ...DEMO_PROFILES[key] });
    setError(null);
  };

  const handleChange = (key, value) => {
    setForm(prev => ({
      ...prev,
      [key]: key === 'applicant_id' ? value : parseFloat(value) || 0
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await assessApplicant(form);
      navigate('/result', { state: { result: res.data, applicant: form } });
    } catch (e) {
      setError('Assessment failed. Make sure the backend is running at localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
      <h2 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>New Application</h2>
      <p style={{ color: '#9ca3af', marginBottom: '32px' }}>Load a demo profile or enter applicant data manually</p>

      {/* Demo Profiles */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '32px' }}>
        {Object.entries(DEMO_PROFILES).map(([key, p]) => (
          <button
            key={key}
            onClick={() => loadProfile(key)}
            style={{
              background: '#111827',
              border: '1px solid #1f2937',
              borderRadius: '12px',
              padding: '16px',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'border-color 0.2s',
            }}
            onMouseEnter={e => e.currentTarget.style.borderColor = '#3b82f6'}
            onMouseLeave={e => e.currentTarget.style.borderColor = '#1f2937'}
          >
            <div style={{ fontSize: '15px', fontWeight: 600, color: '#f9fafb', marginBottom: '6px' }}>{p.label}</div>
            <div style={{ fontSize: '12px', color: p.tagColor, fontWeight: 500 }}>{p.tag}</div>
          </button>
        ))}
      </div>

      {/* Form */}
      <div className="card">
        <div style={{ marginBottom: '20px' }}>
          <label>Applicant ID</label>
          <input
            value={form.applicant_id}
            onChange={e => handleChange('applicant_id', e.target.value)}
          />
        </div>

        {FIELDS.map(group => (
          <div key={group.group} style={{ marginBottom: '24px' }}>
            <h4 style={{
              fontSize: '13px',
              fontWeight: 600,
              color: '#3b82f6',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '16px'
            }}>
              {group.group}
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              {group.fields.map(f => (
                <div key={f.key}>
                  <label>{f.label}</label>
                  <input
                    type="number"
                    step="any"
                    value={form[f.key] ?? 0}
                    onChange={e => handleChange(f.key, e.target.value)}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}

        {error && (
          <div style={{
            background: '#450a0a',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '16px',
            color: '#ef4444',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        <button
          className="btn-primary"
          onClick={handleSubmit}
          disabled={loading}
          style={{ width: '100%', padding: '16px', fontSize: '16px' }}
        >
          {loading ? 'Assessing Application...' : 'Assess Application →'}
        </button>
      </div>
    </div>
  );
}
