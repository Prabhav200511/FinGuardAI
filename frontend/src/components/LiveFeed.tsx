import type { Transaction } from '@/api/client';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';

export function getRiskColor(score: number, threshold = 60) {
  return score >= threshold ? 'text-red-400' : score >= threshold - 20 ? 'text-yellow-400' : 'text-emerald-400';
}
export function getRiskBg(score: number, threshold = 60) {
  return score >= threshold ? 'bg-red-500/10 border-red-500/20' : score >= threshold - 20 ? 'bg-yellow-500/10 border-yellow-500/20' : 'bg-emerald-500/10 border-emerald-500/20';
}
export function getRiskLabel(score: number, threshold = 60) {
  return score >= threshold ? 'HIGH' : score >= threshold - 20 ? 'MED' : 'SAFE';
}

interface LiveFeedProps {
  transactions: Transaction[];
  threshold: number;
}

export function LiveFeed({ transactions, threshold }: LiveFeedProps) {
  if (transactions.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-10 text-center text-slate-400">
        <div className="mb-3 text-4xl opacity-60">📡</div>
        <p className="text-base font-medium text-slate-200">No transactions yet.</p>
        <p className="mt-2 text-sm">Press <strong>Start Live Feed</strong> in the sidebar, or add a demo transaction to begin.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 pr-2">
      <div className="flex items-center justify-between px-1">
        <p className="text-sm text-slate-400">Showing the latest {Math.min(transactions.length, 30)} events</p>
        <div className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.2em] text-emerald-300">
          Live stream
        </div>
      </div>

      {transactions.slice(0, 30).map((t, idx) => {
        const s = t.risk_score || 0;
        const color = getRiskColor(s, threshold);
        const bg = getRiskBg(s, threshold);
        const lbl = getRiskLabel(s, threshold);
        const borderClass = s >= threshold ? 'border-l-4 border-l-red-500' : s >= threshold - 20 ? 'border-l-4 border-l-yellow-500' : 'border-l-4 border-l-emerald-500';
        const statusText = s >= threshold ? 'Needs review' : s >= threshold - 20 ? 'Watchlist' : 'Normal pattern';

        return (
          <Card key={`${t.transaction_id}-${idx}`} className={`bg-slate-900/60 backdrop-blur ${borderClass} overflow-hidden transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-900/80`}>
            <div className="flex flex-col gap-3 p-4 md:flex-row md:items-center">
              <div className="min-w-[120px]">
                <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-slate-500">{t.transaction_id?.substring(0, 14)}</div>
                <div className="mt-1 text-base font-semibold text-slate-100">₹{t.amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
              </div>

              <div className="flex-1 flex flex-wrap gap-3 text-xs text-slate-400">
                <span>🕐 {t.hour.toString().padStart(2, '0')}:00</span>
                <span className="capitalize">🏪 {t.merchant_category}</span>
                <span>📱 {t.device_change ? 'New device' : 'Known device'}</span>
                <span>📍 {t.geo_distance_km.toFixed(0)}km</span>
              </div>

              <div className="flex min-w-[140px] flex-col items-end gap-2">
                <Badge variant="outline" className={`${bg} ${color} w-full justify-center font-bold`}>{lbl} {s.toFixed(0)}</Badge>
                <div className="flex items-center gap-2 text-[11px] text-slate-500">
                  <span className={`h-2 w-2 rounded-full ${s >= threshold ? 'bg-red-500' : s >= threshold - 20 ? 'bg-yellow-500' : 'bg-emerald-500'}`} />
                  {statusText}
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
