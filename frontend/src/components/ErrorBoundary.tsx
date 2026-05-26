import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('App error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-background p-lg">
          <div className="text-center max-w-md">
            <h1 className="font-headline-md text-headline-md text-on-background mb-sm">
              Something went wrong
            </h1>
            <p className="font-body-sm text-on-surface-variant mb-md">
              Please refresh the page. If the problem persists, contact support.
            </p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="bg-primary text-on-primary font-label-md px-lg py-sm rounded-xl"
            >
              Refresh
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
