import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitOverride } from '../api/client';

export default function UnderwriterPanel() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    applicant_id: '',
    original_decision: 'Refer',
    override_decision: 'Approve',
    underwriter_id: '',
    reason: '',
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!form.applicant_id || !form.underwriter_id || !form.reason) {
      setError('Please fill all required fields.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await submitOverride(form);
      setSubmitted(true);
    } catch {
      setError('Failed to submit. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '60px' }}>
        <div style={{
          width: 56, height: 56, borderRadius: '50%',
          border: '1px solid #3FB950',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '24px', margin: '0 auto 20px', color: '#3FB950',
        }}>✓</div>
        <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#3FB950', marginBottom: '8px' }}>
          Override Logged
        </h2>
        <p style={{ color: '#9CA3AF', marginBottom: '28px', fontSize: '14px' }}>
          The underwriter decision has been recorded with a full audit trail.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button
            style={{
              padding: '10px 20px',
              background: '#3B82F6',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '4px',
              fontWeight: 600,
              cursor: 'pointer',
              fontFamily: 'Inter, sans-serif',
            }}
            onClick={() => { setSubmitted(false); setForm({ applicant_id: '', original_decision: 'Refer', override_decision: 'Approve', underwriter_id: '', reason: '' }); }}
          >
            Log Another Override
          </button>
          <button
            style={{
              padding: '10px 20px',
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
            New Application
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '40px 24px' }}>
      <div style={{
        fontSize: '12px',
        fontWeight: 600,
        color: '#9CA3AF',
        letterSpacing: '0.02em',
        marginBottom: '6px',
      }}>
        Compliance Workflow
      </div>
      <h2 style={{ fontSize: '26px', fontWeight: 700, marginBottom: '6px', color: '#FFFFFF' }}>
        Underwriter Override
      </h2>
      <p style={{ color: '#9CA3AF', marginBottom: '28px', fontSize: '14px' }}>
        All overrides are logged with full audit trail for regulatory compliance.
      </p>

      <div style={{
        background: '#1A1A1A',
        border: '1px solid #21262D',
        borderRadius: '6px',
        padding: '24px',
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label style={{ color: '#8B949E' }}>Applicant ID *</label>
            <input value={form.applicant_id}
              onChange={e => setForm(p => ({ ...p, applicant_id: e.target.value }))}
              placeholder="e.g. JAMES_003" />
          </div>
          <div>
            <label style={{ color: '#8B949E' }}>Underwriter ID *</label>
            <input value={form.underwriter_id}
              onChange={e => setForm(p => ({ ...p, underwriter_id: e.target.value }))}
              placeholder="e.g. UW_482" />
          </div>
          <div>
            <label style={{ color: '#8B949E' }}>Original Decision</label>
            <select value={form.original_decision}
              onChange={e => setForm(p => ({ ...p, original_decision: e.target.value }))}>
              <option>Approve</option>
              <option>Refer</option>
              <option>Deny</option>
            </select>
          </div>
          <div>
            <label style={{ color: '#8B949E' }}>Override Decision</label>
            <select value={form.override_decision}
              onChange={e => setForm(p => ({ ...p, override_decision: e.target.value }))}>
              <option>Approve</option>
              <option>Refer</option>
              <option>Deny</option>
            </select>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ color: '#8B949E' }}>Reason for Override *</label>
          <textarea rows={4} value={form.reason}
            onChange={e => setForm(p => ({ ...p, reason: e.target.value }))}
            placeholder="Provide detailed justification for overriding the system decision..."
            style={{ resize: 'vertical' }} />
        </div>

        {error && (
          <div style={{
            background: '#450A0A', border: '1px solid #EF4444',
            borderRadius: '6px', padding: '12px', marginBottom: '16px',
            color: '#EF4444', fontSize: '14px',
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
          {loading ? 'Submitting...' : 'Log Override Decision'}
        </button>
      </div>
    </div>
  );
}
