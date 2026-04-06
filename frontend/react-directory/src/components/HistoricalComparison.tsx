import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { History, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { api } from '../api';
import type { HistoricalAnalysisResponse } from '../types';

export const HistoricalComparison: React.FC = () => {
  const [ticker, setTicker] = useState('');
  const [history, setHistory] = useState<HistoricalAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    try {
      const data = await api.getHistoricalAnalysis(ticker.toUpperCase());
      setHistory(data);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
    });
  };

  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <History size={20} color="#8b5cf6" />
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Historical Comparison</h3>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="Enter ticker (e.g. RELIANCE.NS)"
          style={{
            flex: 1,
            padding: '10px 14px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            background: 'rgba(255,255,255,0.05)',
            color: 'var(--text-primary)',
            fontSize: '14px',
          }}
          onKeyPress={(e) => e.key === 'Enter' && loadHistory()}
        />
        <button
          onClick={loadHistory}
          disabled={loading}
          style={{
            padding: '10px 16px',
            borderRadius: '8px',
            border: 'none',
            background: 'var(--accent-color)',
            color: 'white',
            cursor: 'pointer',
          }}
        >
          {loading ? 'Loading...' : 'Load'}
        </button>
      </div>

      {history && (
        <div>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
            {history.count} historical analyses found for {history.ticker}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflow: 'auto' }}>
            {history.history.map((item, index) => {
              const analysis = item.analysis as any;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  style={{
                    padding: '12px 16px',
                    background: 'rgba(255,255,255,0.03)',
                    borderRadius: '10px',
                    border: '1px solid var(--border-color)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {formatDate(item.created_at)}
                    </span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      {analysis?.recommendation && (
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '10px',
                          fontWeight: 600,
                          background: analysis.recommendation === 'BUY' ? 'rgba(16, 185, 129, 0.2)' : 
                                     analysis.recommendation === 'SELL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                          color: analysis.recommendation === 'BUY' ? '#10b981' : 
                                analysis.recommendation === 'SELL' ? '#ef4444' : '#6b7280',
                        }}>
                          {analysis.recommendation}
                        </span>
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', fontSize: '11px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <Activity size={12} style={{ margin: '0 auto 2px', color: 'var(--text-secondary)' }} />
                      <span style={{ color: 'var(--text-secondary)' }}>Fund:</span>
                      <span style={{ marginLeft: '4px', fontWeight: 500 }}>{analysis?.fundamental?.score ?? 'N/A'}</span>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <TrendingUp size={12} style={{ margin: '0 auto 2px', color: 'var(--text-secondary)' }} />
                      <span style={{ color: 'var(--text-secondary)' }}>Tech:</span>
                      <span style={{ marginLeft: '4px', fontWeight: 500 }}>{analysis?.technical?.score ?? 'N/A'}</span>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <TrendingDown size={12} style={{ margin: '0 auto 2px', color: 'var(--text-secondary)' }} />
                      <span style={{ color: 'var(--text-secondary)' }}>Sent:</span>
                      <span style={{ marginLeft: '4px', fontWeight: 500 }}>{analysis?.sentiment?.score ?? 'N/A'}</span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
