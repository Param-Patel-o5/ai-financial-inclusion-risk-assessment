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
      setError('Please fill all fields');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await submitOverride(form);
      setSubmitted(true);
    } catch (e) {
      setError('Failed to submit override. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div style={{ maxWidth: 600, margin: '80px auto', padding: '0 24px', textAlign: 'center' }}>
        <div style={{ fontSize: '64px', marginBottom: '16px' }}>✓</div>
        <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#10b981', marginBottom: '8px' }}>Override Logged</h2>
        <p style={{ color: '#9ca3af', marginBottom: '32px' }}>
          The underwriter decision has been recorded with a full audit trail.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button
            className="btn-primary"
            onClick={() => {
              setSubmitted(false);
              setForm({
                applicant_id: '',
                original_decision: 'Refer',
                override_decision: 'Approve',
                underwriter_id: '',
                reason: ''
              });
            }}
          >
            New Override
          </button>
          <button className="btn-secondary" onClick={() => navigate('/apply')}>New Application</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: '40px 24px' }}>
      <h2 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>Underwriter Override</h2>
      <p style={{ color: '#9ca3af', marginBottom: '32px' }}>
        Override a system decision with full audit trail logging
      </p>

      <div className="card">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label>Applicant ID</label>
            <input
              value={form.applicant_id}
              onChange={e => setForm(p => ({ ...p, applicant_id: e.target.value }))}
              placeholder="e.g. JAMES_003"
            />
          </div>

          <div>
            <label>Underwriter ID</label>
            <input
              value={form.underwriter_id}
              onChange={e => setForm(p => ({ ...p, underwriter_id: e.target.value }))}
              placeholder="e.g. UW_482"
            />
          </div>

          <div>
            <label>Original Decision</label>
            <select
              value={form.original_decision}
              onChange={e => setForm(p => ({ ...p, original_decision: e.target.value }))}
            >
              <option>Approve</option>
              <option>Refer</option>
              <option>Deny</option>
            </select>
          </div>

          <div>
            <label>Override Decision</label>
            <select
              value={form.override_decision}
              onChange={e => setForm(p => ({ ...p, override_decision: e.target.value }))}
            >
              <option>Approve</option>
              <option>Refer</option>
              <option>Deny</option>
            </select>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label>Reason for Override</label>
          <textarea
            rows={4}
            value={form.reason}
            onChange={e => setForm(p => ({ ...p, reason: e.target.value }))}
            placeholder="Provide a detailed reason for overriding the system decision..."
            style={{ resize: 'vertical' }}
          />
        </div>

        {error && (
          <div style={{
            background: '#450a0a',
            border: '1px solid #ef4444',
            borderRadius: '8px',
            padding: '12px',
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
          style={{ width: '100%', padding: '14px' }}
        >
          {loading ? 'Submitting...' : 'Log Override Decision'}
        </button>
      </div>
    </div>
  );
}
