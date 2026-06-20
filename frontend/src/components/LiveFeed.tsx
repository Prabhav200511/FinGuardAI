import React from 'react';
import type { Transaction } from '@/api/client';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

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
      <div className="text-center py-20 text-slate-400">
        <div className="text-4xl mb-4 opacity-50">📡</div>
        <p>Press <strong>Start Live Feed</strong> in the sidebar, or use controls to add transactions.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 pr-2">
      {transactions.slice(0, 30).map((t, idx) => {
        const s = t.risk_score || 0;
        const color = getRiskColor(s, threshold);
        const bg = getRiskBg(s, threshold);
        const lbl = getRiskLabel(s, threshold);
        const borderClass = s >= threshold ? 'border-l-4 border-l-red-500' : s >= threshold - 20 ? 'border-l-4 border-l-yellow-500' : 'border-l-4 border-l-emerald-500';

        return (
          <Card key={`${t.transaction_id}-${idx}`} className={`bg-card/50 backdrop-blur ${borderClass} overflow-hidden transition-all hover:translate-x-1`}>
            <div className="flex items-center p-3 gap-4">
              <div className="w-24 font-mono text-xs text-slate-500 truncate">{t.transaction_id?.substring(0, 14)}</div>
              <div className="w-24 font-bold text-slate-200">₹{t.amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</div>
              
              <div className="flex-1 flex gap-4 text-xs text-slate-400 flex-wrap">
                <span>🕐 {t.hour.toString().padStart(2, '0')}:00</span>
                <span className="capitalize">🏪 {t.merchant_category}</span>
                <span>📱 {t.device_change ? 'New' : '—'}</span>
                <span>📍 {t.geo_distance_km.toFixed(0)}km</span>
              </div>

              <div className="text-center w-20">
                <Badge variant="outline" className={`${bg} ${color} w-full justify-center font-bold`}>{lbl} {s.toFixed(0)}</Badge>
                <div className="w-full bg-slate-800 h-1.5 mt-1.5 rounded-full overflow-hidden">
                  <div className={`h-full ${s >= threshold ? 'bg-red-500' : s >= threshold - 20 ? 'bg-yellow-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(s, 100)}%` }} />
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
