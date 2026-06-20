import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Zap, CheckCircle, Trash2, StopCircle, PlayCircle, Search } from 'lucide-react';

interface SidebarProps {
  language: string;
  setLanguage: (lang: string) => void;
  liveActive: boolean;
  setLiveActive: (active: boolean) => void;
  onClear: () => void;
  onManualAnalyze: (txn: any) => void;
  onDemoTxn: (type: 'fraud' | 'safe') => void;
}

export function Sidebar({ language, setLanguage, liveActive, setLiveActive, onClear, onManualAnalyze, onDemoTxn }: SidebarProps) {
  const [amt, setAmt] = useState(28000);
  const [geo, setGeo] = useState(820);
  const [vel, setVel] = useState(1);
  const [cat, setCat] = useState("electronics");
  const [hour, setHour] = useState([2]);
  const [dev, setDev] = useState(true);
  const [isNew, setIsNew] = useState(true);

  return (
    <div className="flex flex-col gap-6">
      {/* Live Badge */}
      <div className="flex justify-center">
        {liveActive ? (
          <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-500 ring-1 ring-inset ring-emerald-500/20">
            <span className="mr-1.5 flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            LIVE FEED ACTIVE
          </span>
        ) : (
          <span className="inline-flex items-center rounded-full bg-slate-500/10 px-3 py-1 text-xs font-medium text-slate-500 ring-1 ring-inset ring-slate-500/20">
            <span className="mr-1.5 flex h-2 w-2 rounded-full bg-slate-500"></span>
            FEED PAUSED
          </span>
        )}
      </div>

      {/* Language */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Label>Language / भाषा</Label>
        </div>
        <div className="flex bg-slate-900 p-1 rounded-lg">
          <button 
            className={`flex-1 py-1 text-sm rounded-md transition-all ${language === 'english' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
            onClick={() => setLanguage('english')}
          >English</button>
          <button 
            className={`flex-1 py-1 text-sm rounded-md transition-all ${language === 'hindi' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
            onClick={() => setLanguage('hindi')}
          >हिंदी</button>
        </div>
      </div>

      <hr className="border-border" />

      {/* Demo Controls */}
      <div className="space-y-3">
        <Label>🎮 Demo Controls</Label>
        <p className="text-xs text-muted-foreground">Synthetic txns · no bank connection</p>
        <div className="grid grid-cols-2 gap-2">
          <Button variant="destructive" className="w-full text-xs" onClick={() => onDemoTxn('fraud')}><Zap className="w-3 h-3 mr-1"/> Fraud Txn</Button>
          <Button variant="outline" className="w-full text-xs" onClick={() => onDemoTxn('safe')}><CheckCircle className="w-3 h-3 mr-1"/> Safe Txn</Button>
        </div>
        <Button 
          variant={liveActive ? "secondary" : "default"} 
          className="w-full"
          onClick={() => setLiveActive(!liveActive)}
        >
          {liveActive ? <><StopCircle className="w-4 h-4 mr-2" /> Stop Feed</> : <><PlayCircle className="w-4 h-4 mr-2" /> Start Live Feed</>}
        </Button>
        <Button variant="ghost" className="w-full text-slate-400 hover:text-white" onClick={onClear}>
          <Trash2 className="w-4 h-4 mr-2" /> Clear All
        </Button>
      </div>

      <hr className="border-border" />

      {/* Manual Analysis */}
      <div className="space-y-4">
        <Label className="flex items-center"><Search className="w-4 h-4 mr-2 text-blue-400"/> Manual Analysis</Label>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <Label className="text-xs text-slate-400">Amount (₹)</Label>
            <Input type="number" value={amt} onChange={e => setAmt(Number(e.target.value))} className="h-8 text-sm bg-slate-950" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-slate-400">Distance (km)</Label>
            <Input type="number" value={geo} onChange={e => setGeo(Number(e.target.value))} className="h-8 text-sm bg-slate-950" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-slate-400">Txns / hr</Label>
            <Input type="number" value={vel} onChange={e => setVel(Number(e.target.value))} className="h-8 text-sm bg-slate-950" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs text-slate-400">Category</Label>
            <Select value={cat} onValueChange={setCat}>
              <SelectTrigger className="h-8 text-sm bg-slate-950"><SelectValue /></SelectTrigger>
              <SelectContent>
                {["electronics", "grocery", "restaurant", "fuel", "pharmacy", "transport", "utilities", "clothing", "education"].map(c => 
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="space-y-3 pt-2">
          <div className="flex justify-between">
            <Label className="text-xs text-slate-400">Hour of day: {hour[0]}:00</Label>
          </div>
          <Slider value={hour} onValueChange={setHour} max={23} step={1} />
        </div>
        <div className="grid grid-cols-2 gap-3 pt-2">
          <div className="flex items-center space-x-2">
            <Switch checked={dev} onCheckedChange={setDev} id="new-dev" />
            <Label htmlFor="new-dev" className="text-xs">New Device</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Switch checked={isNew} onCheckedChange={setIsNew} id="new-merch" />
            <Label htmlFor="new-merch" className="text-xs">New Merchant</Label>
          </div>
        </div>
        <Button className="w-full mt-2 bg-blue-600 hover:bg-blue-700" onClick={() => onManualAnalyze({
          transaction_id: "MANUAL-CHECK",
          amount: amt, hour: hour[0], merchant_category: cat,
          device_change: dev ? 1 : 0, geo_distance_km: geo,
          velocity_per_hour: vel, is_new_merchant: isNew ? 1 : 0
        })}>
          Analyze 🔎
        </Button>
      </div>
    </div>
  );
}
