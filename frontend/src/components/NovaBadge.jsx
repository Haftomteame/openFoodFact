export default function NovaBadge({ group }) {
  if (!group) return null;
  return (
    <span className="nova-badge" title={`NOVA groupe ${group}`}>
      {group}
    </span>
  );
}
