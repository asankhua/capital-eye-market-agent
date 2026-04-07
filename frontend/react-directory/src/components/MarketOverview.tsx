import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Globe, Activity, TrendingUp, TrendingDown } from 'lucide-react';
import { api } from '../api';

interface IndexData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
}

export const MarketOverview: React.FC = () => {
  const [indices, setIndices] = useState<IndexData[]>([]);
  const [timestamp, setTimestamp] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadMarketOverview();
  }, []);

  const loadMarketOverview = async () => {
    setLoading(true);
    try {
      const data = await api.getTwelveDataMarketOverview();
      setIndices(data.indices || []);
      setTimestamp(data.timestamp || '');
    } catch (err) {
      setError('Failed to load market overview');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <div style={{ textAlign: 'center', color: '#64748b' }}>
          <Activity size={32} className="animate-spin" style={{ margin: '0 auto 12px' }} />
          <p>Loading market overview...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px', background: '#fee2e2', borderRadius: '12px', color: '#dc2626' }}>
        <p>{error}</p>
        <button 
          onClick={loadMarketOverview}
          style={{
            marginTop: '12px',
            padding: '8px 16px',
            background: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  // Define the exact sequence of indices as requested
  const indexOrder = [
    "NIFTY 50",
    "NIFTY MIDCAP 150",
    "NIFTY SMALLCAP 250",
    "NIFTY ALPHA 50",
    "NIFTY MIDCAP150 MOMENTUM 50",
    "NIFTY50 EQUAL WEIGHT",
    "NIFTY NEXT 50",
    "NIFTY INDIA RAILWAYS PSU",
    "NIFTY BANK",
    "NIFTY IT",
    "NIFTY AUTO",
    "NIFTY PHARMA",
    "NIFTY FMCG",
    "NIFTY METAL",
    "NIFTY REALTY",
    "NIFTY PSU BANK",
    "NIFTY COMMODITIES",
    "INDIA VIX"
  ];

  // Sort indices based on the defined order
  const sortedIndices = [...indices].sort((a: IndexData, b: IndexData) => {
    const indexA = indexOrder.indexOf(a.name);
    const indexB = indexOrder.indexOf(b.name);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        <Globe size={28} color="#2563eb" />
        <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>Market Overview</h2>
      </div>
      {timestamp && (
        <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '24px', marginLeft: '40px' }}>
          Last updated: {new Date(timestamp).toLocaleString('en-IN', { 
            timeZone: 'Asia/Kolkata',
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          })} IST (from NSE)
        </p>
      )}

      {/* Market Indices */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '16px' }}>
          Major Indices
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
          {sortedIndices.map((index) => (
            <motion.div
              key={index.symbol}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                padding: '12px',
                background: '#ffffff',
                borderRadius: '10px',
                border: '1px solid #e5e7eb',
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
              }}
            >
              <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '2px' }}>{index.name}</p>
              <p style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>
                {index.price?.toFixed(2) || 'N/A'}
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                {index.change >= 0 ? (
                  <TrendingUp size={16} color="#059669" />
                ) : (
                  <TrendingDown size={16} color="#dc2626" />
                )}
                <span style={{ 
                  fontSize: '13px', 
                  fontWeight: 600,
                  color: index.change >= 0 ? '#059669' : '#dc2626'
                }}>
                  {index.change >= 0 ? '+' : ''}{index.change?.toFixed(2)} ({index.change_percent?.toFixed(2)}%)
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};
