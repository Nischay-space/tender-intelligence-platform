import { Component, type ErrorInfo, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  error: Error | null
}

export class ErrorBoundary extends Component
  <ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Logged for local debugging; a real deployment would send this
    // to an error-tracking service instead.
    console.error('Dashboard render error:', error, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-paper px-6">
          <div className="max-w-md border border-line bg-white p-6 text-center">
            <h1 className="font-serif text-lg font-semibold text-ink">
              Something went wrong
            </h1>
            <p className="mt-2 text-sm text-slate">
              This part of the dashboard hit an unexpected error. Try
              reloading the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 rounded bg-seal px-3 py-1.5 text-sm font-medium text-paper hover:bg-ink"
            >
              Reload
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}