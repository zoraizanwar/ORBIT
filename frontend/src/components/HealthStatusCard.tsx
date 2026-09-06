import React, { useEffect, useState } from 'react';
import { fetchHealthStatus, HealthResponse } from '../api/health';
import { Activity, Database, Server, RefreshCw, Layers, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export const HealthStatusCard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const loadHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHealthStatus();
      setHealth(data);
      setLastRefreshed(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reach API server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-orbit-emerald border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
          </span>
        );
      case 'degraded':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-orbit-amber border border-amber-500/30">
            <AlertTriangle className="w-3.5 h-3.5" /> Degraded
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-orbit-scarlet border border-red-500/30">
            <XCircle className="w-3.5 h-3.5" /> Unavailable
          </span>
        );
    }
  };

  return (
    <div className="bg-orbit-carbon border border-orbit-border rounded-xl p-6 shadow-2xl max-w-2xl w-full">
      <div className="flex items-center justify-between pb-4 border-b border-orbit-border/60">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-orbit-slate/60 rounded-lg border border-orbit-border">
            <Activity className="w-5 h-5 text-orbit-emerald animate-pulse" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-orbit-text">Local Infrastructure Health</h2>
            <p className="text-xs text-orbit-muted">
              Auto-refreshing every 10s • Last checked: {lastRefreshed.toLocaleTimeString()}
            </p>
          </div>
        </div>
        <button
          onClick={loadHealth}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-orbit-slate hover:bg-slate-700 text-xs font-medium text-orbit-text rounded-md border border-orbit-border transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error ? (
        <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-sm text-red-300">
          <div className="font-semibold mb-1 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-orbit-scarlet" />
            Backend API Disconnected
          </div>
          <p className="text-xs text-orbit-muted">{error}</p>
          <p className="text-xs text-orbit-muted mt-2">
            Ensure FastAPI is running: <code className="text-orbit-emerald">uvicorn app.main:app --reload</code>
          </p>
        </div>
      ) : health ? (
        <div className="mt-6 space-y-4">
          <div className="flex items-center justify-between bg-orbit-slate/30 px-4 py-3 rounded-lg border border-orbit-border/40">
            <span className="text-sm font-medium text-orbit-muted">Overall System State</span>
            {renderStatusBadge(health.status)}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* FastAPI */}
            <div className="bg-orbit-slate/20 p-3.5 rounded-lg border border-orbit-border/40 flex items-start justify-between">
              <div className="flex items-start gap-2.5">
                <Server className="w-4 h-4 text-orbit-cyan mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-orbit-text">FastAPI Core</div>
                  <div className="text-xs text-orbit-muted">v{health.services.api.version || '0.1.0'}</div>
                </div>
              </div>
              {renderStatusBadge(health.services.api.status)}
            </div>

            {/* PostgreSQL */}
            <div className="bg-orbit-slate/20 p-3.5 rounded-lg border border-orbit-border/40 flex items-start justify-between">
              <div className="flex items-start gap-2.5">
                <Database className="w-4 h-4 text-orbit-emerald mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-orbit-text">PostgreSQL 16</div>
                  <div className="text-xs text-orbit-muted">
                    {health.services.database.details || 'Relational Store'}
                  </div>
                </div>
              </div>
              {renderStatusBadge(health.services.database.status)}
            </div>

            {/* PostGIS */}
            <div className="bg-orbit-slate/20 p-3.5 rounded-lg border border-orbit-border/40 flex items-start justify-between">
              <div className="flex items-start gap-2.5">
                <Layers className="w-4 h-4 text-orbit-amber mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-orbit-text">PostGIS 3.4</div>
                  <div className="text-xs text-orbit-muted truncate max-w-[140px]" title={health.services.postgis.details || ''}>
                    {health.services.postgis.details ? 'Spatial Enabled' : 'Spatial Extension'}
                  </div>
                </div>
              </div>
              {renderStatusBadge(health.services.postgis.status)}
            </div>

            {/* Redis */}
            <div className="bg-orbit-slate/20 p-3.5 rounded-lg border border-orbit-border/40 flex items-start justify-between">
              <div className="flex items-start gap-2.5">
                <Activity className="w-4 h-4 text-orbit-scarlet mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-orbit-text">Redis 7.2</div>
                  <div className="text-xs text-orbit-muted">Broker & Tile Cache</div>
                </div>
              </div>
              {renderStatusBadge(health.services.redis.status)}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
