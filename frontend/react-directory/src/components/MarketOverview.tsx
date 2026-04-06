import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Globe, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { api } from '../api';

interface IndexData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
}

interface MoverData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
}

export const MarketOverview: React.FC = () => {
  const [indices, setIndices] = useState<IndexData[]>([]);
  const [gainers, setGainers] = useState<MoverData[]>([]);
  const [losers, setLosers] = useState<MoverData[]>([]);
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
      setGainers(data.top_gainers || []);
      setLosers(data.top_losers || []);
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

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <Globe size={28} color="#2563eb" />
        <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>Market Overview</h2>
      </div>

      {/* Market Indices */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#374151', marginBottom: '16px' }}>
          Major Indices
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          {indices.map((index) => (
            <motion.div
              key={index.symbol}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                padding: '16px',
                background: '#ffffff',
                borderRadius: '12px',
                border: '1px solid #e5e7eb',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}
            >
              <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>{index.name}</p>
              <p style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>
                {index.price?.toFixed(2) || 'N/A'}
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                {index.change >= 0 ? (
                  <TrendingUp size={16} color="#059669" />
                ) : (
                  <TrendingDown size={16} color="#dc2626" />
                )}
                <span style={{ 
                  fontSize: '14px', 
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

      {/* Top Gainers & Losers */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Gainers */}
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#059669', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={20} />
            Top Gainers
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {gainers.slice(0, 5).map((stock, index) => (
              <motion.div
                key={stock.symbol}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                style={{
                  padding: '12px 16px',
                  background: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e5e7eb',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <p style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>{stock.symbol}</p>
                  <p style={{ fontSize: '12px', color: '#6b7280' }}>{stock.name}</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>${stock.price?.toFixed(2)}</p>
                  <p style={{ fontSize: '12px', color: '#059669', fontWeight: 600 }}>
                    +{stock.change_percent?.toFixed(2)}%
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Losers */}
        <div>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#dc2626', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingDown size={20} />
            Top Losers
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {losers.slice(0, 5).map((stock, index) => (
              <motion.div
                key={stock.symbol}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                style={{
                  padding: '12px 16px',
                  background: '#ffffff',
                  borderRadius: '8px',
                  border: '1px solid #e5e7eb',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <p style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>{stock.symbol}</p>
                  <p style={{ fontSize: '12px', color: '#6b7280' }}>{stock.name}</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>${stock.price?.toFixed(2)}</p>
                  <p style={{ fontSize: '12px', color: '#dc2626', fontWeight: 600 }}>
                    {stock.change_percent?.toFixed(2)}%
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
