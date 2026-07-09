export function Card({ className = "", children, ...rest }) {
  return <div className={`card ${className}`} {...rest}>{children}</div>;
}
