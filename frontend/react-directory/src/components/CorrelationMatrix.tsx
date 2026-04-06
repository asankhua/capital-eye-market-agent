import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { GitGraph, Info } from 'lucide-react';
import { api } from '../api';
import type { CorrelationResponse, CorrelationRequest } from '../types';

export const CorrelationMatrix: React.FC = () => {
  const [tickers, setTickers] = useState('');
  const [matrix, setMatrix] = useState<CorrelationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const calculateCorrelation = async () => {
    if (!tickers.trim()) return;
    const tickerList = tickers.split(',').map(t => t.trim().toUpperCase()).filter(Boolean);
    if (tickerList.length < 2) {
      alert('Please enter at least 2 tickers');
      return;
    }
    
    setLoading(true);
    try {
      const request: CorrelationRequest = { tickers: tickerList, period: '1y' };
      const data = await api.getCorrelation(request);
      setMatrix(data);
    } catch (error) {
      console.error('Failed to calculate correlation:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCorrelationColor = (value: number | null) => {
    if (value === null) return '#6b7280';
    if (value > 0.7) return '#10b981'; // Strong positive - green
    if (value > 0.3) return '#f59e0b'; // Moderate - yellow
    if (value > -0.3) return '#6b7280'; // Weak - gray
    if (value > -0.7) return '#f97316'; // Moderate negative - orange
    return '#ef4444'; // Strong negative - red
  };

  const getCorrelationBg = (value: number | null) => {
    if (value === null) return 'rgba(107, 114, 128, 0.1)';
    if (value > 0.7) return 'rgba(16, 185, 129, 0.2)';
    if (value > 0.3) return 'rgba(245, 158, 11, 0.2)';
    if (value > -0.3) return 'rgba(107, 114, 128, 0.2)';
    if (value > -0.7) return 'rgba(249, 115, 22, 0.2)';
    return 'rgba(239, 68, 68, 0.2)';
  };

  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <GitGraph size={20} color="#8b5cf6" />
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Correlation Matrix</h3>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>
          Stock Tickers (comma-separated, min 2)
        </label>
        <input
          type="text"
          value={tickers}
          onChange={(e) => setTickers(e.target.value)}
          placeholder="e.g. RELIANCE.NS, TCS.NS, INFY.NS"
          style={{
            width: '100%',
            padding: '10px 14px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            background: 'rgba(255,255,255,0.05)',
            color: 'var(--text-primary)',
            fontSize: '14px',
          }}
          onKeyPress={(e) => e.key === 'Enter' && calculateCorrelation()}
        />
      </div>

      <button
        onClick={calculateCorrelation}
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
          marginBottom: '16px',
        }}
      >
        {loading ? 'Calculating...' : 'Calculate Correlation'}
      </button>

      {matrix && (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
            <Info size={12} />
            <span>Based on {matrix.data_points} trading days</span>
          </div>
          
          <div style={{ overflow: 'auto', maxWidth: '100%' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr>
                  <th style={{ padding: '8px', borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}></th>
                  {matrix.tickers.map(ticker => (
                    <th key={ticker} style={{ padding: '8px', borderBottom: '1px solid var(--border-color)', textAlign: 'center', fontWeight: 600 }}>
                      {ticker.replace('.NS', '')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {matrix.tickers.map((rowTicker, rowIndex) => (
                  <tr key={rowTicker}>
                    <td style={{ padding: '8px', borderRight: '1px solid var(--border-color)', fontWeight: 600 }}>
                      {rowTicker.replace('.NS', '')}
                    </td>
                    {matrix.tickers.map((colTicker, colIndex) => {
                      const value = matrix.matrix[rowTicker]?.[colTicker];
                      return (
                        <td key={colTicker} style={{ padding: '8px', textAlign: 'center' }}>
                          <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: (rowIndex * matrix.tickers.length + colIndex) * 0.01 }}
                            style={{
                              padding: '6px 8px',
                              borderRadius: '6px',
                              background: getCorrelationBg(value),
                              color: getCorrelationColor(value),
                              fontWeight: 600,
                              fontSize: '11px',
                            }}
                          >
                            {value !== null ? value.toFixed(2) : 'N/A'}
                          </motion.div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap', fontSize: '11px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, background: 'rgba(16, 185, 129, 0.3)' }}></div>
              <span>Strong (+0.7)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, background: 'rgba(245, 158, 11, 0.3)' }}></div>
              <span>Moderate (+0.3)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, background: 'rgba(107, 114, 128, 0.3)' }}></div>
              <span>Weak</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <div style={{ width: 12, height: 12, borderRadius: 3, background: 'rgba(239, 68, 68, 0.3)' }}></div>
              <span>Negative (-0.7)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
