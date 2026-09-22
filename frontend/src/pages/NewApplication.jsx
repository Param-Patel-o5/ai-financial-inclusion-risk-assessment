import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { assessApplicant } from '../api/client';
import AuthModal from '../components/AuthModal';

const INCOME_TYPE_OPTIONS = [
  { value: 0, label: 'Businessman' },
  { value: 1, label: 'Commercial Associate' },
  { value: 2, label: 'Maternity Leave' },
  { value: 3, label: 'Pensioner' },
  { value: 4, label: 'State Servant' },
  { value: 5, label: 'Student' },
  { value: 6, label: 'Unemployed' },
  { value: 7, label: 'Working' },
];

const DEMO_PROFILES = {
  'Priya Sharma': {
    applicant_id: 'PRIYA_001',
    AMT_INCOME_TOTAL: 85000, AMT_CREDIT: 520000, AMT_ANNUITY: 26000,
    credit_income_ratio: 6.12, annuity_income_ratio: 0.31,
    employment_years: 0.8, late_payment_share: 0.05,
    mean_days_late: 2.0, max_days_late: 5.0,
    underpayment_share: 0.04, installments_count: 3.0,
    prev_applications_count: 2.0, prev_refused_count: 1.0,
    prev_refusal_rate: 0.50, thin_file: 1.0,
    bureau_active_credits_count: 0.0, NAME_INCOME_TYPE: 7,
  },
  'Marcus Johnson': {
    applicant_id: 'MARCUS_002',
    AMT_INCOME_TOTAL: 120000, AMT_CREDIT: 680000, AMT_ANNUITY: 34000,
    credit_income_ratio: 5.67, annuity_income_ratio: 0.28,
    employment_years: 2.1, late_payment_share: 0.44,
    mean_days_late: 19.0, max_days_late: 48.0,
    underpayment_share: 0.32, installments_count: 9.0,
    prev_applications_count: 5.0, prev_refused_count: 3.0,
    prev_refusal_rate: 0.60, thin_file: 0.0,
    bureau_active_credits_count: 2.0, NAME_INCOME_TYPE: 7,
  },
  'James Chen': {
    applicant_id: 'JAMES_003',
    AMT_INCOME_TOTAL: 90000, AMT_CREDIT: 579195, AMT_ANNUITY: 23098.5,
    credit_income_ratio: 6.435, annuity_income_ratio: 0.257,
    employment_years: 0.0, late_payment_share: 0.109,
    mean_days_late: 0.362, max_days_late: 9.0,
    underpayment_share: 0.162, installments_count: 210.0,
    prev_applications_count: 8.0, prev_refused_count: 0.0,
    prev_refusal_rate: 0.0, thin_file: 0.0,
    bureau_active_credits_count: 7.0, NAME_INCOME_TYPE: 3,
  },
  'Aisha Patel': {
    applicant_id: 'AISHA_005',
    AMT_INCOME_TOTAL: 90000, AMT_CREDIT: 225000, AMT_ANNUITY: 26833.5,
    credit_income_ratio: 2.50, annuity_income_ratio: 0.298,
    employment_years: 0.95, late_payment_share: 0.0,
    mean_days_late: 0.0, max_days_late: 0.0,
    underpayment_share: 0.0, installments_count: 9.0,
    prev_applications_count: 1.0, prev_refused_count: 0.0,
    prev_refusal_rate: 0.0, thin_file: 1.0,
    bureau_active_credits_count: 0.0, NAME_INCOME_TYPE: 7,
  },
  'Maria Santos': {
    applicant_id: 'MARIA_004',
    AMT_INCOME_TOTAL: 220000, AMT_CREDIT: 280000, AMT_ANNUITY: 14000,
    credit_income_ratio: 1.27, annuity_income_ratio: 0.06,
    employment_years: 7.2, late_payment_share: 0.03,
    mean_days_late: 1.0, max_days_late: 3.0,
    underpayment_share: 0.02, installments_count: 18.0,
    prev_applications_count: 4.0, prev_refused_count: 0.0,
    prev_refusal_rate: 0.0, thin_file: 0.0,
    bureau_active_credits_count: 5.0, NAME_INCOME_TYPE: 7,
  },
};

const PROFILE_META = {
  'Priya Sharma': { color: '#EF4444', tag: 'Thin-File · Deny' },
  'Marcus Johnson': { color: '#EF4444', tag: 'Thick-File · Deny' },
  'James Chen': { color: '#F59E0B', tag: 'Borderline · Refer' },
  'Aisha Patel': { color: '#F59E0B', tag: 'Thin-File · Refer' },
  'Maria Santos': { color: '#10B981', tag: 'Strong · Approve' },
};

const FIELD_GROUPS = [
  {
    group: 'Loan Details', color: '#FFD100', fields: [
      { key: 'AMT_INCOME_TOTAL', label: 'Annual Income (₹)' },
      { key: 'AMT_CREDIT', label: 'Credit Amount (₹)' },
      { key: 'AMT_ANNUITY', label: 'Annual Annuity (₹)' },
      { key: 'credit_income_ratio', label: 'Credit / Income Ratio' },
      { key: 'annuity_income_ratio', label: 'Annuity / Income Ratio' },
    ]
  },
  {
    group: 'Payment History', color: '#EF4444', fields: [
      { key: 'late_payment_share', label: 'Late Payment Share (0–1)' },
      { key: 'mean_days_late', label: 'Mean Days Late' },
      { key: 'max_days_late', label: 'Max Days Late' },
      { key: 'underpayment_share', label: 'Underpayment Share (0–1)' },
      { key: 'installments_count', label: 'Installments Count' },
    ]
  },
  {
    group: 'Credit Profile', color: '#3B82F6', fields: [
      { key: 'prev_applications_count', label: 'Previous Applications' },
      { key: 'prev_refused_count', label: 'Previous Refusals' },
      { key: 'prev_refusal_rate', label: 'Refusal Rate (0–1)' },
      { key: 'thin_file', label: 'Thin File (0 or 1)' },
      { key: 'bureau_active_credits_count', label: 'Active Credits Count' },
    ]
  },
];

export default function NewApplication() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({
    applicant_id: 'APPLICANT_001',
    ...DEMO_PROFILES['James Chen'],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [activeProfile, setActiveProfile] = useState('James Chen');

  useEffect(() => {
    if (location.state?.profile && DEMO_PROFILES[location.state.profile]) {
      setForm(DEMO_PROFILES[location.state.profile]);
      setActiveProfile(location.state.profile);
    }
  }, [location.state]);

  const loadProfile = (name) => {
    setForm({ ...DEMO_PROFILES[name] });
    setActiveProfile(name);
    setError(null);
  };

  const handleChange = (key, value) => {
    setForm(prev => ({
      ...prev,
      [key]: key === 'applicant_id' ? value : parseFloat(value) || 0,
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await assessApplicant(form);
      navigate('/result', { state: { result: res.data, applicant: form } });
    } catch {
      setError('Assessment failed. Ensure backend is running: python -m backend.main');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}

      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'start', marginBottom: '32px',
      }}>
        <div>
          <div className="section-label">Assessment</div>
          <h2 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '4px' }}>
            New Application
          </h2>
          <p style={{ color: '#9CA3AF', fontSize: '14px' }}>
            Load a demo profile or enter data manually.{' '}
            <span
              style={{ color: '#FFD100', cursor: 'pointer', textDecoration: 'underline' }}
              onClick={() => navigate('/dictionary')}
            >
              What do these fields mean?
            </span>
          </p>
        </div>
        <button className="btn-ghost" onClick={() => setShowAuth(true)}>
          🔒 Authenticate Documents
        </button>
      </div>

      {/* Demo Profile Selector — 5 profiles */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: '10px',
        marginBottom: '28px',
      }}>
        {Object.entries(DEMO_PROFILES).map(([name]) => {
          const meta = PROFILE_META[name];
          const isActive = activeProfile === name;
          return (
            <button key={name} onClick={() => loadProfile(name)}
              style={{
                background: isActive ? 'rgba(255,209,0,0.1)' : '#1A1A1A',
                border: `1px solid ${isActive ? '#FFD100' : '#2A2A2A'}`,
                borderRadius: '10px', padding: '14px 12px',
                cursor: 'pointer', textAlign: 'left',
                transition: 'all 0.2s',
              }}
              onMouseEnter={e => {
                if (!isActive) e.currentTarget.style.borderColor = '#555';
              }}
              onMouseLeave={e => {
                if (!isActive) e.currentTarget.style.borderColor = '#2A2A2A';
              }}
            >
              <div style={{
                fontSize: '13px', fontWeight: 600,
                color: '#FFFFFF', marginBottom: '4px',
              }}>{name}</div>
              <div style={{
                fontSize: '11px', color: meta.color,
                fontWeight: 600,
              }}>{meta.tag}</div>
            </button>
          );
        })}
      </div>

      {/* Form */}
      <div className="card">
        <div style={{ marginBottom: '24px' }}>
          <label>Applicant ID</label>
          <input
            value={form.applicant_id}
            onChange={e => handleChange('applicant_id', e.target.value)}
          />
        </div>

        {/* Employment group with dropdown */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <div style={{ width: 3, height: 14, background: '#10B981', borderRadius: '2px' }} />
            <span className="section-label" style={{ marginBottom: 0 }}>Employment</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div>
              <label>Income Type</label>
              <select
                value={form.NAME_INCOME_TYPE}
                onChange={e => handleChange('NAME_INCOME_TYPE', e.target.value)}
              >
                {INCOME_TYPE_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label>Employment Years</label>
              <input type="number" step="any"
                value={form.employment_years ?? 0}
                onChange={e => handleChange('employment_years', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Remaining field groups */}
        {FIELD_GROUPS.map(group => (
          <div key={group.group} style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <div style={{ width: 3, height: 14, background: group.color, borderRadius: '2px' }} />
              <span className="section-label" style={{ marginBottom: 0 }}>{group.group}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
              {group.fields.map(f => (
                <div key={f.key}>
                  <label>{f.label}</label>
                  <input type="number" step="any"
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
            background: '#450A0A', border: '1px solid #EF4444',
            borderRadius: '8px', padding: '12px 16px',
            marginBottom: '16px', color: '#EF4444', fontSize: '14px',
          }}>{error}</div>
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