import { Link } from 'react-router-dom'

export function BrandLogo({ className = '' }: { className?: string }) {
  return (
    <Link to="/" className={`flex items-center gap-2 shrink-0 ${className}`}>
      <img src="/logo-icon.png" alt="" className="h-9 w-9 object-contain" aria-hidden />
      <span className="font-headline-sm text-headline-sm font-bold tracking-wide text-on-background">
        BREATHE ESG
      </span>
    </Link>
  )
}
