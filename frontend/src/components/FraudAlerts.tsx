import React, { useState } from 'react';
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
      <div className="text-center py-20 text-slate-400">
        <div className="text-4xl mb-4 opacity-50">🔍</div>
        <p>No fraud alerts yet. Add a suspicious transaction or start the live feed.</p>
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
      setExplanations(prev => ({ ...prev, [key]: "Error generating explanation." }));
    }
    setLoadingExp(prev => ({ ...prev, [key]: false }));
  };

  return (
    <div className="flex flex-col gap-4 pr-2">
      <p className="text-sm text-slate-400">Showing {alerts.length} fraud alert{alerts.length !== 1 ? 's' : ''}</p>
      
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
          <Card key={`${alert.transaction_id}-${idx}`} className={`bg-card/60 backdrop-blur border-l-4 ${isHigh ? 'border-l-red-500 shadow-lg shadow-red-500/10' : 'border-l-yellow-500 shadow-lg shadow-yellow-500/10'}`}>
            <CardHeader className="pb-2">
              <div className="flex justify-between items-center">
                <CardTitle className="text-base font-bold text-slate-100 flex items-center gap-3">
                  <span className="opacity-50">#{idx + 1}</span> {alert.transaction_id?.substring(0, 20)}
                  <Badge className={`${bg} ${color}`}>{isHigh ? 'HIGH RISK' : 'MEDIUM RISK'}</Badge>
                </CardTitle>
                <span className="text-xs text-slate-500">{alert.ts || new Date().toISOString()}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-6 text-sm text-slate-400 border-t border-border pt-3 mb-4 flex-wrap">
                <span>💰 <strong className="text-slate-200">₹{alert.amount.toLocaleString('en-IN')}</strong></span>
                <span>🕐 {alert.hour.toString().padStart(2, '0')}:00</span>
                <span className="capitalize">🏪 {alert.merchant_category}</span>
                <span>📱 {alert.device_change ? 'Changed' : 'Same'}</span>
                <span>📍 {alert.geo_distance_km.toFixed(0)} km</span>
                <span>⚡ {alert.velocity_per_hour} txns/hr</span>
                <span>🎯 Score: <strong className={color}>{s.toFixed(1)}</strong>/100</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
                {/* SHAP Chart */}
                <div className="md:col-span-5 bg-black/20 p-4 rounded-lg border border-border/50">
                  <p className="text-xs text-slate-400 mb-2">🔍 SHAP Risk Factors (🔴 risk | 🟢 normal)</p>
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
                                  <div className="bg-slate-900 border border-slate-800 p-2 rounded text-xs shadow-xl">
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
                    <p className="text-xs text-slate-500 italic py-4">SHAP values not available.</p>
                  )}
                </div>

                {/* AI Explanation */}
                <div className="md:col-span-7 flex flex-col items-start h-full">
                  {!explanations[expKey] && !loadingExp[expKey] ? (
                    <Button onClick={() => handleExplain(alert, idx)} variant="secondary" className="mt-4">
                      <Bot className="w-4 h-4 mr-2" /> 
                      {language === 'hindi' ? 'स्पष्टीकरण देखें' : 'Get AI Explanation'}
                    </Button>
                  ) : loadingExp[expKey] ? (
                    <div className="flex items-center text-sm text-slate-400 mt-4 animate-pulse">
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Generating explanation...
                    </div>
                  ) : (
                    <div className="w-full">
                      <div className="bg-blue-950/20 border border-blue-900/50 p-4 rounded-lg text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                        {explanations[expKey]}
                      </div>
                      <Button onClick={() => handleExplain(alert, idx)} variant="ghost" size="sm" className="mt-2 text-xs text-slate-500 hover:text-slate-300">
                        <RefreshCw className="w-3 h-3 mr-2" />
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
