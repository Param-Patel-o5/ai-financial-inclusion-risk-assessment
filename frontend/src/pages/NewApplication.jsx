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
  'Maria Santos': {
    applicant_id: 'MARIA_001',
    AMT_INCOME_TOTAL: 240000, AMT_CREDIT: 200000, AMT_ANNUITY: 10000,
    credit_income_ratio: 0.83, annuity_income_ratio: 0.04,
    employment_years: 8.5, late_payment_share: 0.0,
    mean_days_late: 0.0, max_days_late: 0.0,
    underpayment_share: 0.0, installments_count: 36.0,
    prev_applications_count: 2.0, prev_refused_count: 0.0,
    prev_refusal_rate: 0.0, thin_file: 0.0,
    bureau_active_credits_count: 6.0, NAME_INCOME_TYPE: 7,
  },
  'Priya Sharma': {
    applicant_id: 'PRIYA_002',
    AMT_INCOME_TOTAL: 160000, AMT_CREDIT: 100000, AMT_ANNUITY: 5000,
    credit_income_ratio: 0.625, annuity_income_ratio: 0.031,
    employment_years: 4.0, late_payment_share: 0.0,
    mean_days_late: 0.0, max_days_late: 0.0,
    underpayment_share: 0.0, installments_count: 15.0,
    prev_applications_count: 1.0, prev_refused_count: 0.0,
    prev_refusal_rate: 0.0, thin_file: 1.0,
    bureau_active_credits_count: 0.0, NAME_INCOME_TYPE: 7,
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
  'Marcus Johnson': {
    applicant_id: 'MARCUS_004',
    AMT_INCOME_TOTAL: 120000, AMT_CREDIT: 680000, AMT_ANNUITY: 34000,
    credit_income_ratio: 5.67, annuity_income_ratio: 0.28,
    employment_years: 2.1, late_payment_share: 0.44,
    mean_days_late: 19.0, max_days_late: 48.0,
    underpayment_share: 0.32, installments_count: 9.0,
    prev_applications_count: 5.0, prev_refused_count: 3.0,
    prev_refusal_rate: 0.60, thin_file: 0.0,
    bureau_active_credits_count: 2.0, NAME_INCOME_TYPE: 7,
  },
  'David Vance': {
    applicant_id: 'DAVID_005',
    AMT_INCOME_TOTAL: 75000, AMT_CREDIT: 540000, AMT_ANNUITY: 27000,
    credit_income_ratio: 7.20, annuity_income_ratio: 0.36,
    employment_years: 0.4, late_payment_share: 0.25,
    mean_days_late: 8.5, max_days_late: 22.0,
    underpayment_share: 0.20, installments_count: 6.0,
    prev_applications_count: 6.0, prev_refused_count: 4.0,
    prev_refusal_rate: 0.67, thin_file: 0.0,
    bureau_active_credits_count: 3.0, NAME_INCOME_TYPE: 7,
  },
};

const PROFILE_META = {
  'Maria Santos': { color: '#10B981', tag: 'Prime / Approve' },
  'Priya Sharma': { color: '#10B981', tag: 'Thin-File Hero / Approve' },
  'James Chen': { color: '#F59E0B', tag: 'Borderline / Refer' },
  'Marcus Johnson': { color: '#EF4444', tag: 'Delinquency / Deny' },
  'David Vance': { color: '#EF4444', tag: 'Inquiry Velocity / Deny' },
};

export default function NewApplication() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({
    applicant_id: 'PRIYA_002',
    ...DEMO_PROFILES['Priya Sharma'],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [activeProfile, setActiveProfile] = useState('Priya Sharma');

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
    setForm(prev => {
      const parsedVal = key === 'applicant_id' ? value : parseFloat(value) || 0;
      const next = { ...prev, [key]: parsedVal };

      // Automatically keep derived ratios in sync
      if (key === 'AMT_INCOME_TOTAL' || key === 'AMT_CREDIT' || key === 'AMT_ANNUITY') {
        const inc = key === 'AMT_INCOME_TOTAL' ? parsedVal : (prev.AMT_INCOME_TOTAL || 1);
        const cred = key === 'AMT_CREDIT' ? parsedVal : prev.AMT_CREDIT;
        const ann = key === 'AMT_ANNUITY' ? parsedVal : prev.AMT_ANNUITY;
        if (inc > 0) {
          next.credit_income_ratio = parseFloat((cred / inc).toFixed(3));
          next.annuity_income_ratio = parseFloat((ann / inc).toFixed(3));
        }
      }

      return next;
    });
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
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '28px',
      }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '6px', color: '#FFFFFF' }}>
            New Application
          </h2>
          <p style={{ color: '#9CA3AF', fontSize: '14px', margin: 0 }}>
            Load a demo profile or enter data manually.
          </p>
        </div>
        <button
          style={{
            background: 'transparent',
            border: '1px solid #30363D',
            color: '#FFFFFF',
            padding: '8px 16px',
            borderRadius: '4px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: 'pointer',
            fontFamily: 'Inter, sans-serif',
            transition: 'border-color 0.15s ease',
          }}
          onMouseEnter={e => e.currentTarget.style.borderColor = '#4B5563'}
          onMouseLeave={e => e.currentTarget.style.borderColor = '#30363D'}
          onClick={() => setShowAuth(true)}
        >
          Authenticate Documents
        </button>
      </div>

      {/* Demo Profile Selector — 5 profiles */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: '10px',
        marginBottom: '24px',
      }}>
        {Object.entries(DEMO_PROFILES).map(([name]) => {
          const meta = PROFILE_META[name];
          const isActive = activeProfile === name;
          return (
            <button key={name} onClick={() => loadProfile(name)}
              style={{
                background: '#161B22',
                border: `1px solid ${isActive ? '#3B82F6' : '#2A2A2A'}`,
                borderRadius: '6px',
                padding: '14px 12px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'border-color 0.15s ease',
              }}
              onMouseEnter={e => {
                if (!isActive) e.currentTarget.style.borderColor = '#4B5563';
              }}
              onMouseLeave={e => {
                if (!isActive) e.currentTarget.style.borderColor = '#2A2A2A';
              }}
            >
              <div style={{
                fontSize: '13px',
                fontWeight: 600,
                color: '#FFFFFF',
                marginBottom: '4px',
              }}>
                {name}
              </div>
              <div style={{
                fontSize: '11px',
                color: meta.color,
                fontWeight: 600,
              }}>
                {meta.tag}
              </div>
            </button>
          );
        })}
      </div>

      {/* Form Container */}
      <div style={{
        background: '#1A1A1A',
        border: '1px solid #21262D',
        borderRadius: '6px',
        padding: '24px',
      }}>
        <div style={{ marginBottom: '24px' }}>
          <label style={{ color: '#8B949E' }}>Applicant ID</label>
          <input
            value={form.applicant_id}
            onChange={e => handleChange('applicant_id', e.target.value)}
          />
        </div>

        {/* Employment group */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            fontSize: '12px',
            color: '#8B949E',
            fontWeight: 600,
            letterSpacing: '0.02em',
            borderBottom: '1px solid #21262D',
            paddingBottom: '6px',
            marginBottom: '16px',
          }}>
            Employment
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div>
              <label style={{ color: '#8B949E' }}>Income Type</label>
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
              <label style={{ color: '#8B949E' }}>Employment Years</label>
              <input type="number" step="any"
                value={form.employment_years ?? 0}
                onChange={e => handleChange('employment_years', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Loan Details group */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            fontSize: '12px',
            color: '#8B949E',
            fontWeight: 600,
            letterSpacing: '0.02em',
            borderBottom: '1px solid #21262D',
            paddingBottom: '6px',
            marginBottom: '16px',
          }}>
            Loan Details
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div>
              <label style={{ color: '#8B949E' }}>Annual Income (₹)</label>
              <input type="number" step="any"
                value={form.AMT_INCOME_TOTAL ?? 0}
                onChange={e => handleChange('AMT_INCOME_TOTAL', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Credit Amount (₹)</label>
              <input type="number" step="any"
                value={form.AMT_CREDIT ?? 0}
                onChange={e => handleChange('AMT_CREDIT', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Annual Annuity (₹)</label>
              <input type="number" step="any"
                value={form.AMT_ANNUITY ?? 0}
                onChange={e => handleChange('AMT_ANNUITY', e.target.value)}
              />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label style={{ color: '#8B949E', margin: 0 }}>Credit / Income Ratio</label>
                <span style={{ fontSize: '11px', color: '#6B7280', fontFamily: "'IBM Plex Mono', monospace" }}>calculated</span>
              </div>
              <input
                type="number"
                readOnly
                value={form.credit_income_ratio ?? 0}
                style={{
                  background: '#0D1117',
                  color: '#8B949E',
                  border: '1px solid #21262D',
                  cursor: 'default',
                  outline: 'none',
                }}
              />
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label style={{ color: '#8B949E', margin: 0 }}>Annuity / Income Ratio</label>
                <span style={{ fontSize: '11px', color: '#6B7280', fontFamily: "'IBM Plex Mono', monospace" }}>calculated</span>
              </div>
              <input
                type="number"
                readOnly
                value={form.annuity_income_ratio ?? 0}
                style={{
                  background: '#0D1117',
                  color: '#8B949E',
                  border: '1px solid #21262D',
                  cursor: 'default',
                  outline: 'none',
                }}
              />
            </div>
          </div>
        </div>

        {/* Payment History group */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            fontSize: '12px',
            color: '#8B949E',
            fontWeight: 600,
            letterSpacing: '0.02em',
            borderBottom: '1px solid #21262D',
            paddingBottom: '6px',
            marginBottom: '16px',
          }}>
            Payment History
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div>
              <label style={{ color: '#8B949E' }}>Late Payment Share (0–1)</label>
              <input type="number" step="any"
                value={form.late_payment_share ?? 0}
                onChange={e => handleChange('late_payment_share', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Mean Days Late</label>
              <input type="number" step="any"
                value={form.mean_days_late ?? 0}
                onChange={e => handleChange('mean_days_late', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Max Days Late</label>
              <input type="number" step="any"
                value={form.max_days_late ?? 0}
                onChange={e => handleChange('max_days_late', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Underpayment Share (0–1)</label>
              <input type="number" step="any"
                value={form.underpayment_share ?? 0}
                onChange={e => handleChange('underpayment_share', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Installments Count</label>
              <input type="number" step="any"
                value={form.installments_count ?? 0}
                onChange={e => handleChange('installments_count', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Credit Profile group */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{
            fontSize: '12px',
            color: '#8B949E',
            fontWeight: 600,
            letterSpacing: '0.02em',
            borderBottom: '1px solid #21262D',
            paddingBottom: '6px',
            marginBottom: '16px',
          }}>
            Credit Profile
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div>
              <label style={{ color: '#8B949E' }}>Previous Applications</label>
              <input type="number" step="any"
                value={form.prev_applications_count ?? 0}
                onChange={e => handleChange('prev_applications_count', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Previous Refusals</label>
              <input type="number" step="any"
                value={form.prev_refused_count ?? 0}
                onChange={e => handleChange('prev_refused_count', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Refusal Rate (0–1)</label>
              <input type="number" step="any"
                value={form.prev_refusal_rate ?? 0}
                onChange={e => handleChange('prev_refusal_rate', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Thin File (0 or 1)</label>
              <input type="number" step="any"
                value={form.thin_file ?? 0}
                onChange={e => handleChange('thin_file', e.target.value)}
              />
            </div>
            <div>
              <label style={{ color: '#8B949E' }}>Active Credits Count</label>
              <input type="number" step="any"
                value={form.bureau_active_credits_count ?? 0}
                onChange={e => handleChange('bureau_active_credits_count', e.target.value)}
              />
            </div>
          </div>
        </div>

        {error && (
          <div style={{
            background: '#450A0A',
            border: '1px solid #EF4444',
            borderRadius: '6px',
            padding: '12px 16px',
            marginBottom: '16px',
            color: '#EF4444',
            fontSize: '14px',
          }}>{error}</div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: '100%',
            padding: '14px',
            fontSize: '15px',
            fontWeight: 600,
            background: '#3B82F6',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontFamily: 'Inter, sans-serif',
            transition: 'background 0.2s',
          }}
          onMouseEnter={e => {
            if (!loading) e.currentTarget.style.background = '#2563EB';
          }}
          onMouseLeave={e => {
            if (!loading) e.currentTarget.style.background = '#3B82F6';
          }}
        >
          {loading ? 'Assessing Application...' : 'Assess Application'}
        </button>
      </div>
    </div>
  );
}