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
          width: 72, height: 72, borderRadius: '50%',
          background: '#064E3B', border: '2px solid #10B981',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '32px', margin: '0 auto 20px', color: '#10B981',
        }}>✓</div>
        <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#10B981', marginBottom: '8px' }}>
          Override Logged
        </h2>
        <p style={{ color: '#9CA3AF', marginBottom: '32px' }}>
          The underwriter decision has been recorded with a full audit trail.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button className="btn-primary" onClick={() => { setSubmitted(false); setForm({ applicant_id: '', original_decision: 'Refer', override_decision: 'Approve', underwriter_id: '', reason: '' }); }}>
            Log Another Override
          </button>
          <button className="btn-secondary" onClick={() => navigate('/apply')}>New Application</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '40px 24px' }}>
      <div className="section-label">Compliance Workflow</div>
      <h2 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '4px' }}>Underwriter Override</h2>
      <p style={{ color: '#9CA3AF', marginBottom: '32px', fontSize: '14px' }}>
        All overrides are logged with full audit trail for regulatory compliance.
      </p>

      <div className="card">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label>Applicant ID *</label>
            <input value={form.applicant_id}
              onChange={e => setForm(p => ({ ...p, applicant_id: e.target.value }))}
              placeholder="e.g. JAMES_003" />
          </div>
          <div>
            <label>Underwriter ID *</label>
            <input value={form.underwriter_id}
              onChange={e => setForm(p => ({ ...p, underwriter_id: e.target.value }))}
              placeholder="e.g. UW_482" />
          </div>
          <div>
            <label>Original Decision</label>
            <select value={form.original_decision}
              onChange={e => setForm(p => ({ ...p, original_decision: e.target.value }))}>
              <option>Approve</option>
              <option>Refer</option>
              <option>Deny</option>
            </select>
          </div>
          <div>
            <label>Override Decision</label>
            <select value={form.override_decision}
              onChange={e => setForm(p => ({ ...p, override_decision: e.target.value }))}>
              <option>Approve</option>
              <option>Refer</option>
              <option>Deny</option>
            </select>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label>Reason for Override *</label>
          <textarea rows={4} value={form.reason}
            onChange={e => setForm(p => ({ ...p, reason: e.target.value }))}
            placeholder="Provide detailed justification for overriding the system decision..."
            style={{ resize: 'vertical' }} />
        </div>

        {error && (
          <div style={{
            background: '#450A0A', border: '1px solid #EF4444',
            borderRadius: '8px', padding: '12px', marginBottom: '16px',
            color: '#EF4444', fontSize: '14px',
          }}>{error}</div>
        )}

        <button className="btn-primary" onClick={handleSubmit} disabled={loading}
          style={{ width: '100%', padding: '14px' }}>
          {loading ? 'Submitting...' : 'Log Override Decision'}
        </button>
      </div>
    </div>
  );
}
