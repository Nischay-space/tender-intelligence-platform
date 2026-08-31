import { Link } from 'react-router-dom'

export interface Crumb {
  label: string
  to?: string
}

interface BreadcrumbsProps {
  trail: Crumb[]
}

export function Breadcrumbs({ trail }: BreadcrumbsProps) {
  return (
    <nav aria-label="Breadcrumb" className="mb-4 text-sm text-slate">
      {trail.map((crumb, index) => {
        const isLast = index === trail.length - 1

        return (
          <span key={`${crumb.label}-${index}`}>
            {crumb.to && !isLast ? (
              <Link to={crumb.to} className="hover:text-ink hover:underline">
                {crumb.label}
              </Link>
            ) : (
              <span className={isLast ? 'text-ink' : undefined}>
                {crumb.label}
              </span>
            )}
            {!isLast && <span className="mx-2 text-line">/</span>}
          </span>
        )
      })}
    </nav>
  )
}
