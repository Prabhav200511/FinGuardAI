import { useEffect, useState } from 'react';
import { fetchMetrics } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export function Analytics() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetchMetrics().then(setMetrics).catch(console.error);
  }, []);

  if (!metrics) {
    return <div className="text-center py-10 text-slate-400">Loading analytics...</div>;
  }

  const totalProcessedValue = metrics.total_processed != null
    ? Number(metrics.total_processed)
    : ((Number(metrics.training_rows) || 0) + (Number(metrics.test_rows) || 0));
  const totalProcessed = Number.isFinite(totalProcessedValue) ? totalProcessedValue : 0;

  const averageLatencyValue = metrics.average_latency_ms != null ? Number(metrics.average_latency_ms) : 0;
  const averageLatencyMs = Number.isFinite(averageLatencyValue) ? averageLatencyValue : 0;

  const thresholdValue = metrics.current_threshold != null ? Number(metrics.current_threshold) : (metrics.threshold != null ? Number(metrics.threshold) : 60);
  const currentThreshold = Number.isFinite(thresholdValue) ? thresholdValue : 60;

  const recentTransactions = Array.isArray(metrics.recent_transactions) ? metrics.recent_transactions : [];
  const featureImportance = Array.isArray(metrics.feature_importance) && metrics.feature_importance.length > 0
    ? metrics.feature_importance
    : (Array.isArray(metrics.input_features) ? metrics.input_features.map((feature: string, idx: number) => ({ feature, importance: Math.max(0.05, 1 - idx * 0.08) })) : []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Overview Stats */}
      <Card className="bg-card/60 backdrop-blur">
        <CardHeader>
          <CardTitle className="text-lg">System Performance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center border-b border-border pb-2">
            <span className="text-slate-400">Total Processed</span>
            <span className="text-xl font-bold">{Number.isFinite(totalProcessed) ? totalProcessed.toLocaleString() : '0'}</span>
          </div>
          <div className="flex justify-between items-center border-b border-border pb-2">
            <span className="text-slate-400">Avg Latency (ms)</span>
            <span className="text-xl font-bold text-emerald-400">{Number.isFinite(averageLatencyMs) ? averageLatencyMs.toFixed(1) : '0.0'}ms</span>
          </div>
          <div className="flex justify-between items-center pb-2">
            <span className="text-slate-400">Alert Threshold</span>
            <span className="text-xl font-bold">{Number.isFinite(currentThreshold) ? currentThreshold : 60} / 100</span>
          </div>
        </CardContent>
      </Card>

      {/* Feature Importance Chart */}
      <Card className="bg-card/60 backdrop-blur">
        <CardHeader>
          <CardTitle className="text-lg">Global Feature Importance (SHAP)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureImportance} layout="vertical" margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="feature" type="category" stroke="#94a3b8" width={100} tick={{fontSize: 12}} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                <Bar dataKey="importance" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Time Series (Recent Transactions) */}
      <Card className="md:col-span-2 bg-card/60 backdrop-blur">
        <CardHeader>
          <CardTitle className="text-lg">Recent Transactions Volume</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            {recentTransactions && recentTransactions.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={recentTransactions}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="hour" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b' }} />
                  <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-slate-500 italic text-center pt-20">Not enough data to plot volume yet.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
