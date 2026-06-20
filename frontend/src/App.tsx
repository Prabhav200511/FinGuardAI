import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Sidebar } from './components/Sidebar';
import { LiveFeed } from './components/LiveFeed';
import { FraudAlerts } from './components/FraudAlerts';
import { Analytics } from './components/Analytics';
import { fetchDemoFeed, fetchPrediction, type Transaction } from './api/client';
import { ShieldCheck } from 'lucide-react';

const THRESHOLD = 65;

export default function App() {
  const [activeTab, setActiveTab] = useState<'live' | 'alerts' | 'analytics'>('live');
  const [language, setLanguage] = useState('english');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [liveActive, setLiveActive] = useState(false);
  const [stats, setStats] = useState({ total: 0, alerts: 0 });

  /** Add a transaction that already has risk_score (from demo feed) */
  const addEnrichedTransaction = useCallback((txn: Transaction) => {
    const enriched = { ...txn, ts: new Date().toLocaleTimeString() };
    setTransactions(prev => [enriched, ...prev]);
    setStats(prev => ({
      total: prev.total + 1,
      alerts: prev.alerts + ((txn.risk_score ?? 0) >= THRESHOLD ? 1 : 0),
    }));
  }, []);

  /** Run a manual transaction through /predict then add it */
  const handleManualAnalyze = useCallback(async (txn: Transaction) => {
    try {
      const result = await fetchPrediction(txn);
      addEnrichedTransaction({ ...txn, ...result });
      setActiveTab('live');
    } catch (e) {
      console.error('Manual prediction error:', e);
    }
  }, [addEnrichedTransaction]);

  /** Insert a single demo fraud or safe transaction */
  const handleDemoTxn = useCallback(async (type: 'fraud' | 'safe') => {
    try {
      // Demo feed items already come back with risk_score from the API
      const feed = await fetchDemoFeed(1, type === 'fraud' ? 1.0 : 0.0);
      if (feed && feed.length > 0) {
        addEnrichedTransaction(feed[0]);
      }
    } catch (e) {
      console.error('Demo txn error:', e);
    }
  }, [addEnrichedTransaction]);

  const handleClear = useCallback(() => {
    setTransactions([]);
    setStats({ total: 0, alerts: 0 });
  }, []);

  // Live demo feed loop
  useEffect(() => {
    if (!liveActive) return;

    let cancelled = false;

    const tick = async () => {
      try {
        const feed = await fetchDemoFeed(1, 0.3);
        if (!cancelled && feed && feed.length > 0) {
          addEnrichedTransaction(feed[0]);
        }
      } catch (e) {
        console.error('Live feed error:', e);
      }
    };

    const interval = setInterval(tick, 3000);
    // Fire one immediately so you don't wait 3s for first result
    tick();

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [liveActive, addEnrichedTransaction]);

  const fraudAlerts = transactions.filter(t => (t.risk_score ?? 0) >= THRESHOLD);

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-200 flex overflow-hidden font-sans selection:bg-blue-500/30">
      {/* Sidebar */}
      <div className="w-80 border-r border-slate-800 bg-slate-900/40 p-4 flex flex-col gap-6 backdrop-blur-xl shrink-0 z-10 h-screen overflow-hidden">
        <div className="text-center pb-4 border-b border-slate-800/60 pt-2">
          <div className="flex items-center justify-center gap-2 mb-1">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
              FinGuard AI
            </h1>
          </div>
          <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em] font-semibold">UPI Fraud Detection · XAI</p>
        </div>
        <ScrollArea className="flex-1">
          <div className="pr-4">
            <Sidebar
              language={language} setLanguage={setLanguage}
              liveActive={liveActive} setLiveActive={setLiveActive}
              onClear={handleClear} onManualAnalyze={handleManualAnalyze}
              onDemoTxn={handleDemoTxn}
            />
          </div>
        </ScrollArea>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {/* Background glow effects */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[100px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-600/10 blur-[100px] pointer-events-none" />

        {/* Top Stats Row */}
        <div className="p-6 pb-2 sticky top-0 z-20 flex gap-4">
          <Card className="flex-1 bg-slate-900/40 backdrop-blur-md border-slate-800/60 shadow-xl">
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-400 uppercase tracking-widest font-semibold mb-1">Total Monitored</div>
                <div className="text-4xl font-bold text-slate-100">{stats.total}</div>
              </div>
              <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                <span className="text-blue-400 text-xl">📡</span>
              </div>
            </CardContent>
          </Card>
          <Card className="flex-1 bg-slate-900/40 backdrop-blur-md border-slate-800/60 shadow-xl">
            <CardContent className="p-5 flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-400 uppercase tracking-widest font-semibold mb-1">Fraud Alerts</div>
                <div className="text-4xl font-bold text-red-400">{stats.alerts}</div>
              </div>
              <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center border border-red-500/20 animate-pulse">
                <span className="text-red-400 text-xl">🚨</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <div className="px-6 py-4 flex gap-2 border-b border-slate-800/50">
          <Button
            variant={activeTab === 'live' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('live')}
            className={activeTab === 'live' ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-900/20' : 'text-slate-400 hover:text-slate-200'}
          >
            📡 Live Feed
          </Button>
          <Button
            variant={activeTab === 'alerts' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('alerts')}
            className={activeTab === 'alerts' ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-900/20' : 'text-slate-400 hover:text-slate-200'}
          >
            🚨 Fraud Alerts {stats.alerts > 0 && <span className="ml-2 bg-red-950 text-red-400 px-1.5 py-0.5 rounded-full text-xs border border-red-800/50">{stats.alerts}</span>}
          </Button>
          <Button
            variant={activeTab === 'analytics' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('analytics')}
            className={activeTab === 'analytics' ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-900/20' : 'text-slate-400 hover:text-slate-200'}
          >
            📊 Analytics
          </Button>
        </div>

        {/* Tab Content — this is the main scrollable area */}
        <div className="flex-1 overflow-y-auto p-6 relative z-10">
          <div className="max-w-6xl mx-auto pb-12">
            {activeTab === 'live' && <LiveFeed transactions={transactions} threshold={THRESHOLD} />}
            {activeTab === 'alerts' && <FraudAlerts alerts={fraudAlerts} threshold={THRESHOLD} language={language} />}
            {activeTab === 'analytics' && <Analytics />}
          </div>
        </div>
      </div>
    </div>
  );
}
