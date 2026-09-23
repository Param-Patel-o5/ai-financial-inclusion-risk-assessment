import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/', label: 'Home' },
  { to: '/apply', label: 'New Application' },
  { to: '/dictionary', label: 'Data Guide' },
  { to: '/fairness', label: 'Fairness' },
  { to: '/underwriter', label: 'Underwriter' },
];

export default function Navbar() {
  const location = useLocation();
  return (
    <nav style={{
      background: '#111111',
      borderBottom: '1px solid #2A2A2A',
      padding: '0 32px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: '64px',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: 38, height: 38,
          background: '#FFD100',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 800,
          fontSize: '15px',
          color: '#0A0A0A',
          letterSpacing: '-0.5px',
        }}>FT</div>
        <div>
          <div style={{ fontWeight: 700, fontSize: '16px', color: '#FFFFFF', lineHeight: 1.2 }}>
            FairTrace
          </div>
          <div style={{ fontSize: '10px', color: '#FFD100', fontWeight: 600, letterSpacing: '0.05em' }}>
            BY SYNCHRONY
          </div>
        </div>
      </Link>

      {/* Nav Links */}
      <div style={{ display: 'flex', gap: '8px', height: '100%', alignItems: 'center' }}>
        {links.map(link => {
          const active = location.pathname === link.to;
          return (
            <Link key={link.to} to={link.to} style={{
              padding: '0 12px',
              height: '64px',
              display: 'flex',
              alignItems: 'center',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: active ? 600 : 400,
              color: active ? '#FFFFFF' : '#9CA3AF',
              background: 'transparent',
              borderBottom: active ? '2px solid #FFB700' : '2px solid transparent',
              transition: 'color 0.15s ease, border-color 0.15s ease',
              boxSizing: 'border-box',
            }}
            onMouseEnter={e => {
              if (!active) e.currentTarget.style.color = '#D1D5DB';
            }}
            onMouseLeave={e => {
              if (!active) e.currentTarget.style.color = '#9CA3AF';
            }}
            >
              {link.label}
            </Link>
          );
        })}
      </div>

      {/* Right side */}
      <div style={{ fontSize: '12px', color: '#6B7280', fontWeight: 500, opacity: 0.6 }}>
        v1.0.0 · Demo Mode
      </div>
    </nav>
  );
}
