import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity, ArrowUpDown, Clock } from 'lucide-react';
import { api } from '../api';

interface Mover {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
}

type MoverType = 'gainers' | 'losers' | 'active';

export const MarketMovers: React.FC = () => {
  const [movers, setMovers] = useState<Mover[]>([]);
  const [type, setType] = useState<MoverType>('gainers');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    loadMovers();
  }, [type]);

  const loadMovers = async () => {
    setLoading(true);
    try {
      const data = await api.getNSEMarketMovers(type);
      setMovers(data.movers || []);
      setLastUpdated(`${new Date().toLocaleString('en-IN', { 
        timeZone: 'Asia/Kolkata',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })} IST (from ${data.source || 'NSE'})`);
    } catch (err) {
      setError('Failed to load market movers');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const tabs: { id: MoverType; label: string; icon: React.ReactNode; color: string }[] = [
    { id: 'gainers', label: 'Top Gainers', icon: <TrendingUp size={18} />, color: '#059669' },
    { id: 'losers', label: 'Top Losers', icon: <TrendingDown size={18} />, color: '#dc2626' },
    { id: 'active', label: 'Most Active', icon: <ArrowUpDown size={18} />, color: '#2563eb' },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <div style={{ textAlign: 'center', color: '#64748b' }}>
          <Activity size={32} className="animate-spin" style={{ margin: '0 auto 12px' }} />
          <p>Loading market movers...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px', background: '#fee2e2', borderRadius: '12px', color: '#dc2626' }}>
        <p>{error}</p>
        <button 
          onClick={loadMovers}
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

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <ArrowUpDown size={28} color="#2563eb" />
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>Market Movers</h2>
          {lastUpdated && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px', fontSize: '12px', color: '#6b7280' }}>
              <Clock size={12} />
              <span>Last updated: {lastUpdated}</span>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setType(tab.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              background: type === tab.id ? tab.color : '#f3f4f6',
              color: type === tab.id ? '#ffffff' : '#374151',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Movers List - 5x4 Grid Layout (5 columns, 4 rows = 20 stocks) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
        {movers.map((mover, index) => (
          <motion.div
            key={mover.symbol}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            style={{
              padding: '16px',
              background: '#ffffff',
              borderRadius: '12px',
              border: '1px solid #e5e7eb',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div>
              <p style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>{mover.symbol}</p>
              <p style={{ fontSize: '13px', color: '#6b7280', marginTop: '2px' }}>{mover.name}</p>
              <p style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                Vol: {(mover.volume / 1000000).toFixed(1)}M
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <p style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>
                ₹{mover.price?.toFixed(2)}
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end', marginTop: '4px' }}>
                {mover.change >= 0 ? (
                  <TrendingUp size={16} color="#059669" />
                ) : (
                  <TrendingDown size={16} color="#dc2626" />
                )}
                <span style={{ 
                  fontSize: '14px', 
                  fontWeight: 600,
                  color: mover.change >= 0 ? '#059669' : '#dc2626'
                }}>
                  {mover.change >= 0 ? '+' : ''}{mover.change_percent?.toFixed(2)}%
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {movers.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <p>No data available. Please check your API key configuration.</p>
        </div>
      )}
    </div>
  );
};
