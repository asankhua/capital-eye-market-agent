import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Newspaper, Clock, TrendingUp, TrendingDown } from 'lucide-react';
import { api } from '../api';

interface MarketMover {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
}

export const NewsInsights: React.FC = () => {
  const [gainers, setGainers] = useState<MarketMover[]>([]);
  const [losers, setLosers] = useState<MarketMover[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    loadMarketData();
  }, []);

  const loadMarketData = async () => {
    setLoading(true);
    try {
      // Load Indian market movers from NSE
      const [gainersData, losersData] = await Promise.all([
        api.getNSEMarketMovers('gainers'),
        api.getNSEMarketMovers('losers')
      ]);
      setGainers(gainersData.movers || []);
      setLosers(losersData.movers || []);
      setLastUpdated(`${new Date().toLocaleString('en-IN', { 
        timeZone: 'Asia/Kolkata',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })} IST (from NSE)`);
    } catch (err) {
      setError('Failed to load market data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <div style={{ textAlign: 'center', color: '#64748b' }}>
          <Newspaper size={32} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
          <p>Loading market data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px', background: '#fee2e2', borderRadius: '12px', color: '#dc2626' }}>
        <p>{error}</p>
        <button 
          onClick={loadMarketData}
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
        <Newspaper size={28} color="#2563eb" />
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

      {/* Gainers Section */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#059669', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <TrendingUp size={20} /> Top Gainers
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
          gap: '12px',
          maxWidth: '100%',
          overflowX: 'hidden'
        }}>
          {gainers.slice(0, 10).map((item, index) => (
            <motion.div
              key={`gainer-${index}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              style={{
                padding: '14px',
                background: '#ecfdf5',
                borderRadius: '10px',
                border: '1px solid #a7f3d0',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '16px', fontWeight: 700, color: '#065f46' }}>{item.symbol}</span>
                <span style={{ fontSize: '14px', fontWeight: 600, color: '#059669', background: '#d1fae5', padding: '2px 8px', borderRadius: '4px' }}>
                  +{item.change_percent.toFixed(2)}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: '#047857' }}>
                <span>Rs. {item.price.toFixed(2)}</span>
                <span>+{item.change.toFixed(2)}</span>
              </div>
              <div style={{ fontSize: '11px', color: '#065f46' }}>
                Vol: {(item.volume / 100000).toFixed(2)}L
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Losers Section */}
      <div>
        <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#dc2626', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <TrendingDown size={20} /> Top Losers
        </h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
          gap: '12px',
          maxWidth: '100%',
          overflowX: 'hidden'
        }}>
          {losers.slice(0, 10).map((item, index) => (
            <motion.div
              key={`loser-${index}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              style={{
                padding: '14px',
                background: '#fef2f2',
                borderRadius: '10px',
                border: '1px solid #fecaca',
                display: 'flex',
                flexDirection: 'column',
                gap: '6px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '16px', fontWeight: 700, color: '#991b1b' }}>{item.symbol}</span>
                <span style={{ fontSize: '14px', fontWeight: 600, color: '#dc2626', background: '#fee2e2', padding: '2px 8px', borderRadius: '4px' }}>
                  {item.change_percent.toFixed(2)}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: '#b91c1c' }}>
                <span>Rs. {item.price.toFixed(2)}</span>
                <span>{item.change.toFixed(2)}</span>
              </div>
              <div style={{ fontSize: '11px', color: '#991b1b' }}>
                Vol: {(item.volume / 100000).toFixed(2)}L
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {gainers.length === 0 && losers.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <Newspaper size={48} style={{ margin: '0 auto 16px', opacity: 0.3 }} />
          <p>No market data available at the moment. Please try again later.</p>
          {error && <p style={{ fontSize: '12px', marginTop: '8px', color: '#ef4444' }}>{error}</p>}
        </div>
      )}
    </div>
  );
};
