import { useState } from 'react';
import { fetchExplanation, type Transaction } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getRiskColor, getRiskBg } from './LiveFeed';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Bot, RefreshCw } from 'lucide-react';

interface FraudAlertsProps {
  alerts: Transaction[];
  threshold: number;
  language: string;
}

export function FraudAlerts({ alerts, threshold, language }: FraudAlertsProps) {
  const [explanations, setExplanations] = useState<Record<string, string>>({});
  const [loadingExp, setLoadingExp] = useState<Record<string, boolean>>({});

  if (alerts.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-10 text-center text-slate-400">
        <div className="mb-3 text-4xl opacity-60">🔍</div>
        <p className="text-base font-medium text-slate-200">No fraud alerts yet.</p>
        <p className="mt-2 text-sm">Add a suspicious transaction or start the live feed to populate the review queue.</p>
      </div>
    );
  }

  const handleExplain = async (t: Transaction, idx: number) => {
    const key = `${t.transaction_id}-${idx}-${language}`;
    setLoadingExp(prev => ({ ...prev, [key]: true }));
    try {
      const res = await fetchExplanation({ ...t, language });
      setExplanations(prev => ({ ...prev, [key]: res.explanation }));
    } catch (e) {
      setExplanations(prev => ({ ...prev, [key]: 'Error generating explanation.' }));
    }
    setLoadingExp(prev => ({ ...prev, [key]: false }));
  };

  return (
    <div className="flex flex-col gap-4 pr-2">
      <div className="flex items-center justify-between rounded-xl border border-slate-800/60 bg-slate-900/40 px-4 py-3">
        <p className="text-sm text-slate-400">Showing {alerts.length} fraud alert{alerts.length !== 1 ? 's' : ''}</p>
        <div className="rounded-full border border-red-500/20 bg-red-500/10 px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.2em] text-red-300">
          Review queue
        </div>
      </div>

      {alerts.map((alert, idx) => {
        const s = alert.risk_score || 0;
        const color = getRiskColor(s, threshold);
        const bg = getRiskBg(s, threshold);
        const isHigh = s >= threshold;
        const expKey = `${alert.transaction_id}-${idx}-${language}`;

        const shapData = (alert.top_features || []).map(f => ({
          name: language === 'hindi' ? f.label_hi : f.label_en,
          value: Math.abs(f.shap_value),
          increasesRisk: f.increases_risk,
          displayValue: f.display_value
        }));

        return (
          <Card key={`${alert.transaction_id}-${idx}`} className={`bg-slate-900/60 backdrop-blur border-l-4 ${isHigh ? 'border-l-red-500 shadow-lg shadow-red-500/10' : 'border-l-yellow-500 shadow-lg shadow-yellow-500/10'}`}>
            <CardHeader className="pb-2">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <CardTitle className="flex items-center gap-3 text-base font-bold text-slate-100">
                  <span className="opacity-50">#{idx + 1}</span> {alert.transaction_id?.substring(0, 20)}
                  <Badge className={`${bg} ${color}`}>{isHigh ? 'HIGH RISK' : 'MEDIUM RISK'}</Badge>
                </CardTitle>
                <span className="text-xs text-slate-500">{alert.ts || new Date().toISOString()}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex flex-wrap gap-4 border-t border-border/60 pt-3 text-sm text-slate-400">
                <span>💰 <strong className="text-slate-200">₹{alert.amount.toLocaleString('en-IN')}</strong></span>
                <span>🕐 {alert.hour.toString().padStart(2, '0')}:00</span>
                <span className="capitalize">🏪 {alert.merchant_category}</span>
                <span>📱 {alert.device_change ? 'Changed' : 'Same'}</span>
                <span>📍 {alert.geo_distance_km.toFixed(0)} km</span>
                <span>⚡ {alert.velocity_per_hour} txns/hr</span>
                <span>🎯 Score: <strong className={color}>{s.toFixed(1)}</strong>/100</span>
              </div>

              <div className="grid grid-cols-1 gap-6 md:grid-cols-12 md:items-start">
                <div className="rounded-lg border border-border/50 bg-black/20 p-4 md:col-span-5">
                  <p className="mb-2 text-xs text-slate-400">🔍 SHAP Risk Factors (🔴 risk | 🟢 normal)</p>
                  {shapData.length > 0 ? (
                    <div className="h-40">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={shapData} layout="vertical" margin={{ top: 0, right: 30, left: 10, bottom: 0 }}>
                          <XAxis type="number" hide />
                          <YAxis dataKey="name" type="category" width={80} tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
                          <Tooltip
                            content={({ active, payload }) => {
                              if (active && payload && payload.length) {
                                return (
                                  <div className="rounded border border-slate-800 bg-slate-900 p-2 text-xs shadow-xl">
                                    <p className="text-slate-300">{payload[0].payload.name}</p>
                                    <p className="font-bold text-slate-100">{payload[0].payload.displayValue}</p>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Bar dataKey="value" barSize={16} radius={[0, 4, 4, 0]}>
                            {shapData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.increasesRisk ? '#f87171' : '#34d399'} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <p className="py-4 text-xs italic text-slate-500">SHAP values not available.</p>
                  )}
                </div>

                <div className="flex h-full flex-col items-start md:col-span-7">
                  {!explanations[expKey] && !loadingExp[expKey] ? (
                    <Button onClick={() => handleExplain(alert, idx)} variant="secondary" className="mt-4 rounded-xl">
                      <Bot className="mr-2 h-4 w-4" />
                      {language === 'hindi' ? 'स्पष्टीकरण देखें' : 'Get AI Explanation'}
                    </Button>
                  ) : loadingExp[expKey] ? (
                    <div className="mt-4 flex items-center text-sm text-slate-400 animate-pulse">
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generating explanation...
                    </div>
                  ) : (
                    <div className="w-full">
                      <div className="rounded-lg border border-blue-900/50 bg-blue-950/20 p-4 text-sm leading-relaxed text-slate-300 whitespace-pre-wrap">
                        {explanations[expKey]}
                      </div>
                      <Button onClick={() => handleExplain(alert, idx)} variant="ghost" size="sm" className="mt-2 rounded-xl text-xs text-slate-500 hover:text-slate-300">
                        <RefreshCw className="mr-2 h-3 w-3" />
                        {language === 'hindi' ? 'पुनः उत्पन्न' : 'Regenerate'}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
