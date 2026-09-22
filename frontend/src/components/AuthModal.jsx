export default function AuthModal({ onClose }) {
  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: 'rgba(0,0,0,0.8)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000,
    }} onClick={onClose}>
      <div className="card" style={{ maxWidth: 480, width: '90%', padding: '32px' }}
        onClick={e => e.stopPropagation()}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>🔒</div>
          <h3 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px' }}>
            Document Verification
          </h3>
          <p style={{ color: '#9CA3AF', fontSize: '14px', lineHeight: 1.6 }}>
            In production, applicants can upload supporting documents
            to verify their entered data before assessment.
          </p>
        </div>

        <div style={{ background: '#111111', borderRadius: '10px', padding: '16px', marginBottom: '24px' }}>
          <div style={{ fontSize: '13px', color: '#FFD100', fontWeight: 600, marginBottom: '12px' }}>
            SUPPORTED DOCUMENTS (Coming Soon)
          </div>
          {[
            '📄 Income Tax Returns / Salary Slips',
            '🏦 Bank Statements (6 months)',
            '📋 Employment Verification Letter',
            '💳 Bureau Report Authorization',
          ].map(doc => (
            <div key={doc} style={{
              padding: '8px 0',
              borderBottom: '1px solid #2A2A2A',
              fontSize: '14px', color: '#9CA3AF',
              display: 'flex', alignItems: 'center', gap: '8px'
            }}>{doc}</div>
          ))}
        </div>

        <div style={{
          background: 'rgba(255,209,0,0.05)',
          border: '1px solid rgba(255,209,0,0.2)',
          borderRadius: '8px', padding: '12px',
          fontSize: '13px', color: '#9CA3AF',
          marginBottom: '20px', lineHeight: 1.6,
        }}>
          This feature is under development. For this demo,
          please enter applicant data manually or use a demo profile.
        </div>

        <button className="btn-primary" onClick={onClose} style={{ width: '100%' }}>
          Continue with Manual Entry
        </button>
      </div>
    </div>
  );
}
