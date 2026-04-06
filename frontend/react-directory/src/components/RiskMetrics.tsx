import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Activity, TrendingUp, AlertTriangle } from 'lucide-react';
import { api } from '../api';
import type { RiskMetricsResponse, RiskMetricsRequest } from '../types';

export const RiskMetrics: React.FC = () => {
  const [tickers, setTickers] = useState('');
  const [metrics, setMetrics] = useState<RiskMetricsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const calculateMetrics = async () => {
    if (!tickers.trim()) return;
    const tickerList = tickers.split(',').map(t => t.trim().toUpperCase()).filter(Boolean);
    if (tickerList.length === 0) return;
    
    setLoading(true);
    try {
      const request: RiskMetricsRequest = { tickers: tickerList, period: '1y' };
      const data = await api.getRiskMetrics(request);
      setMetrics(data);
    } catch (error) {
      console.error('Failed to calculate risk metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <Shield size={20} color="#ef4444" />
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Risk Metrics</h3>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>
          Stock Tickers (comma-separated)
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
          onKeyPress={(e) => e.key === 'Enter' && calculateMetrics()}
        />
      </div>

      <button
        onClick={calculateMetrics}
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
        {loading ? 'Calculating...' : 'Calculate Risk Metrics'}
      </button>

      {metrics && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Sharpe Ratio */}
          <div>
            <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <TrendingUp size={14} />
              Sharpe Ratio (Risk-adjusted return)
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {metrics.sharpe_ratios.map((item, index) => (
                <motion.div
                  key={item.ticker}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px',
                    background: 'rgba(255,255,255,0.03)',
                    borderRadius: '6px',
                    fontSize: '12px',
                  }}
                >
                  <span>{item.ticker}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Return: {item.annual_return?.toFixed(1)}%</span>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontWeight: 600,
                      background: (item.sharpe_ratio || 0) > 1 ? 'rgba(16, 185, 129, 0.2)' : 
                                 (item.sharpe_ratio || 0) > 0 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                      color: (item.sharpe_ratio || 0) > 1 ? '#10b981' : 
                            (item.sharpe_ratio || 0) > 0 ? '#f59e0b' : '#ef4444',
                    }}>
                      {item.sharpe_ratio?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Beta */}
          <div>
            <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={14} />
              Beta (Market Sensitivity)
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {metrics.betas.map((item, index) => (
                <motion.div
                  key={item.ticker}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 + 0.1 }}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px',
                    background: 'rgba(255,255,255,0.03)',
                    borderRadius: '6px',
                    fontSize: '12px',
                  }}
                >
                  <span>{item.ticker}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>{item.interpretation}</span>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontWeight: 600,
                      background: (item.beta || 1) > 1.5 ? 'rgba(239, 68, 68, 0.2)' : 
                                 (item.beta || 1) < 0.8 ? 'rgba(59, 130, 246, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                      color: (item.beta || 1) > 1.5 ? '#ef4444' : 
                            (item.beta || 1) < 0.8 ? '#3b82f6' : '#10b981',
                    }}>
                      β {item.beta?.toFixed(2) || 'N/A'}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* VaR */}
          <div>
            <h4 style={{ fontSize: '13px', fontWeight: 600, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertTriangle size={14} />
              Value at Risk (95% confidence)
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {metrics.var_metrics.map((item, index) => (
                <motion.div
                  key={item.ticker}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 + 0.2 }}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px',
                    background: 'rgba(255,255,255,0.03)',
                    borderRadius: '6px',
                    fontSize: '12px',
                  }}
                >
                  <span>{item.ticker}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    Max daily loss: <strong style={{ color: '#ef4444' }}>₹{item.var_amount?.toFixed(0) || 'N/A'}</strong>
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
