export default function StatusBadge({ status }) {
  const normalized = status?.toLowerCase() || 'refer';
  const badgeClass = `badge-${normalized}`;

  return (
    <span className={badgeClass}>
      {status?.toUpperCase() || 'REFER'}
    </span>
  );
}
