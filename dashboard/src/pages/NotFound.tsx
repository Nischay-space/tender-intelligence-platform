import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="py-12 text-center">
      <h1 className="font-serif text-2xl font-semibold text-ink">
        Page not found
      </h1>
      <p className="mt-2 text-slate">
        There's nothing here. The tender you're looking for may have
        moved, or the link is out of date.
      </p>
      <Link
        to="/"
        className="mt-4 inline-block text-sm text-seal hover:underline"
      >
        Back to Overview
      </Link>
    </div>
  )
}