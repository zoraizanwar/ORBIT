import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error in UI:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-orbit-void text-orbit-text flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-orbit-carbon border border-orbit-scarlet/50 rounded-lg p-6 shadow-xl">
            <h2 className="text-xl font-bold text-orbit-scarlet mb-2">Workstation UI Exception</h2>
            <p className="text-orbit-muted text-sm mb-4">
              An unhandled rendering error occurred. Please refresh or check local server logs.
            </p>
            <pre className="bg-orbit-slate p-3 rounded text-xs text-red-300 overflow-x-auto mb-4">
              {this.state.error?.message || 'Unknown error'}
            </pre>
            <button
              onClick={() => window.location.reload()}
              className="w-full py-2 bg-orbit-emerald text-orbit-void font-semibold rounded hover:bg-emerald-400 transition"
            >
              Reload Workstation
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
