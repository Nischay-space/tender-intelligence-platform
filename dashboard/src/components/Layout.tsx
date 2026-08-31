import { NavLink, Outlet } from 'react-router-dom'
import { getTenderStats } from '../api/client'
import { useAsync } from '../hooks/useAsync'

const NAV_ITEMS = [
  { to: '/', label: 'Overview', end: true },
  { to: '/tenders', label: 'Tenders', end: false },
]

function SidebarLink({
  to,
  label,
  end,
}: {
  to: string
  label: string
  end: boolean
}) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `block rounded px-3 py-2 text-sm transition-colors ${
          isActive
            ? 'bg-seal/20 font-medium text-seal-light'
            : 'text-paper/70 hover:bg-white/5 hover:text-paper'
        }`
      }
    >
      {label}
    </NavLink>
  )
}

export function Layout() {
  const { data: stats } = useAsync(getTenderStats, [])

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-60 flex-shrink-0 flex-col bg-ink px-4 py-6">
        <div className="px-3">
          <span className="font-serif text-lg font-semibold text-paper">
            Tender Intelligence
          </span>
        </div>

        <nav className="mt-8 space-y-1">
          {NAV_ITEMS.map((item) => (
            <SidebarLink key={item.to} {...item} />
          ))}
        </nav>

        <div className="mt-auto px-3 pt-8 text-xs text-paper/50">
          {stats
            ? `${stats.total} tender${stats.total === 1 ? '' : 's'} tracked`
            : '\u00A0'}
        </div>
      </aside>

      <div className="flex-1 bg-paper">
        <main className="mx-auto max-w-5xl px-8 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
