export function Spinner({ className = "" }) {
  return (
    <div
      className={`inline-block animate-spin rounded-full border-2 border-slate-300 border-t-brand-600 ${className}`}
      style={{ width: "1.25rem", height: "1.25rem" }}
      role="status"
      aria-label="loading"
    />
  );
}
