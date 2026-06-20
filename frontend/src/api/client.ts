// In production the frontend is served from the same origin as the API.
// In development Vite proxies /api to localhost:8000.
export const API_BASE_URL = '/api';

export interface Transaction {
  transaction_id?: string;
  amount: number;
  hour: number;
  merchant_category: string;
  device_change: number;
  geo_distance_km: number;
  velocity_per_hour: number;
  is_new_merchant: number;
  language?: string;
  // enriched after prediction
  ts?: string;
  risk_score?: number;
  is_fraud?: boolean;
  top_features?: Array<{
    feature: string;
    shap_value: number;
    increases_risk: boolean;
    display_value: string;
    label_en: string;
    label_hi: string;
  }>;
  explanation?: string;
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE_URL}/model/metrics`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  return res.json();
}

/**
 * Fetches demo transactions from the API.
 * The API returns items shaped as:
 *   { transaction: { amount, hour, ... }, risk_score, is_fraud, top_features, ... }
 * We flatten them into Transaction objects.
 */
export async function fetchDemoFeed(n = 15, fraud_ratio = 0.35): Promise<Transaction[]> {
  const res = await fetch(`${API_BASE_URL}/demo/feed?n=${n}&fraud_ratio=${fraud_ratio}`);
  if (!res.ok) throw new Error('Failed to fetch demo feed');
  const items = await res.json();
  return items.map((item: any) => ({
    ...item.transaction,
    risk_score: item.risk_score,
    is_fraud: item.is_fraud,
    top_features: item.top_features,
    transaction_id: item.transaction?.transaction_id || item.transaction_id || `TXN-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
  }));
}

export async function fetchPrediction(txn: Transaction) {
  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(txn),
  });
  if (!res.ok) throw new Error('Failed to fetch prediction');
  return res.json();
}

export async function fetchExplanation(txn: Transaction) {
  const res = await fetch(`${API_BASE_URL}/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(txn),
  });
  if (!res.ok) throw new Error('Failed to fetch explanation');
  return res.json();
}
