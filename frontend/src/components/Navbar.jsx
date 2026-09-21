import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/apply', label: 'New Application' },
  { to: '/fairness', label: 'Fairness' },
  { to: '/underwriter', label: 'Underwriter' },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <nav style={{
      background: '#111827',
      borderBottom: '1px solid #1f2937',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: '64px',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          width: 32,
          height: 32,
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '16px'
        }}>⚖</div>
        <span style={{ fontWeight: 700, fontSize: '18px', color: '#f9fafb' }}>
          FairLend <span style={{ color: '#3b82f6' }}>AI</span>
        </span>
      </div>

      <div style={{ display: 'flex', gap: '4px' }}>
        {links.map(link => (
          <Link
            key={link.to}
            to={link.to}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: 500,
              color: location.pathname === link.to ? '#3b82f6' : '#9ca3af',
              background: location.pathname === link.to ? '#1e3a5f' : 'transparent',
              transition: 'all 0.2s',
            }}
          >
            {link.label}
          </Link>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#10b981' }}>
        <div style={{ width: 8, height: 8, background: '#10b981', borderRadius: '50%' }} />
        API Live
      </div>
    </nav>
  );
}
