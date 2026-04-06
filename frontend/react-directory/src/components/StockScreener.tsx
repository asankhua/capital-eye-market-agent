import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Filter, Search } from 'lucide-react';
import { api } from '../api';
import type { ScreenerResult, ScreenerRequest } from '../types';

export const StockScreener: React.FC = () => {
  const [criteria, setCriteria] = useState<ScreenerRequest>({
    limit: 20,
  });
  const [results, setResults] = useState<ScreenerResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const runScreen = async () => {
    setLoading(true);
    setHasSearched(true);
    try {
      const response = await api.screenStocks(criteria);
      setResults(response.results);
    } catch (error) {
      console.error('Screening failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num?: number) => {
    if (num === undefined || num === null) return 'N/A';
    if (num >= 1e9) return `₹${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e7) return `₹${(num / 1e7).toFixed(1)}Cr`;
    if (num >= 1e6) return `₹${(num / 1e6).toFixed(1)}M`;
    return num.toFixed(2);
  };

  const formatPercent = (num?: number) => {
    if (num === undefined || num === null) return 'N/A';
    return `${(num * 100).toFixed(1)}%`;
  };

  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <Filter size={20} color="#10b981" />
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Stock Screener</h3>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '12px',
        marginBottom: '16px' 
      }}>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px', display: 'block' }}>
            Min P/E
          </label>
          <input
            type="number"
            value={criteria.min_pe || ''}
            onChange={(e) => setCriteria({...criteria, min_pe: e.target.value ? parseFloat(e.target.value) : undefined})}
            placeholder="e.g. 10"
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'rgba(255,255,255,0.05)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
          />
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px', display: 'block' }}>
            Max P/E
          </label>
          <input
            type="number"
            value={criteria.max_pe || ''}
            onChange={(e) => setCriteria({...criteria, max_pe: e.target.value ? parseFloat(e.target.value) : undefined})}
            placeholder="e.g. 30"
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'rgba(255,255,255,0.05)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
          />
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px', display: 'block' }}>
            Min Market Cap (Cr)
          </label>
          <input
            type="number"
            value={criteria.min_market_cap || ''}
            onChange={(e) => setCriteria({...criteria, min_market_cap: e.target.value ? parseFloat(e.target.value) : undefined})}
            placeholder="e.g. 1000"
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'rgba(255,255,255,0.05)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
          />
        </div>
        <div>
          <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px', display: 'block' }}>
            Min Profit Margin
          </label>
          <input
            type="number"
            step="0.01"
            value={criteria.min_profit_margin || ''}
            onChange={(e) => setCriteria({...criteria, min_profit_margin: e.target.value ? parseFloat(e.target.value) : undefined})}
            placeholder="e.g. 0.1"
            style={{
              width: '100%',
              padding: '8px 12px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'rgba(255,255,255,0.05)',
              color: 'var(--text-primary)',
              fontSize: '13px',
            }}
          />
        </div>
      </div>

      <button
        onClick={runScreen}
        disabled={loading}
        style={{
          width: '100%',
          padding: '12px',
          borderRadius: '8px',
          border: 'none',
          background: 'var(--accent-color)',
          color: 'white',
          fontWeight: 500,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          marginBottom: '16px',
        }}
      >
        <Search size={16} />
        {loading ? 'Screening...' : 'Run Screen'}
      </button>

      {hasSearched && (
        <div>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
            Found {results.length} stocks matching criteria
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflow: 'auto' }}>
            {results.map((stock, index) => (
              <motion.div
                key={stock.ticker}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
                style={{
                  padding: '12px 16px',
                  background: 'rgba(255,255,255,0.03)',
                  borderRadius: '10px',
                  border: '1px solid var(--border-color)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div>
                    <span style={{ fontWeight: 600, fontSize: '14px' }}>{stock.ticker}</span>
                    <p style={{ fontSize: '11px', color: 'var(--text-secondary)', margin: 0 }}>{stock.company_name}</p>
                  </div>
                  <span style={{ fontSize: '13px', fontWeight: 500 }}>{formatNumber(stock.current_price)}</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', fontSize: '11px' }}>
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>P/E:</span>
                    <span style={{ marginLeft: '4px' }}>{stock.pe_ratio?.toFixed(1) || 'N/A'}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>Margin:</span>
                    <span style={{ marginLeft: '4px' }}>{formatPercent(stock.profit_margin)}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>ROE:</span>
                    <span style={{ marginLeft: '4px' }}>{formatPercent(stock.roe)}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
