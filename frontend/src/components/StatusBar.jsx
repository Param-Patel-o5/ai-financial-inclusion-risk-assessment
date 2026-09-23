import { useEffect, useState } from 'react';
import { getHealth } from '../api/client';

export default function StatusBar() {
  const [ok, setOk] = useState(null);

  useEffect(() => {
    getHealth()
      .then(() => setOk(true))
      .catch(() => setOk(false));
  }, []);

  if (ok === null) return null;

  return (
    <div style={{
      width: '100%',
      background: '#111111',
      borderBottom: '1px solid #2A2A2A',
      padding: '6px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      fontSize: '12px',
      fontWeight: 500,
      color: '#9CA3AF',
    }}>
      <div style={{
        width: 7, height: 7,
        borderRadius: '50%',
        background: ok ? '#10B981' : '#EF4444',
        animation: ok ? 'pulse 2s infinite' : 'none',
      }} />
      {ok
        ? 'FairTrace API | All Systems Operational | ECOA | Reg B | FCRA Compliant'
        : 'API Offline | Start backend with: python -m backend.main'}
      <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }`}</style>
    </div>
  );
}
