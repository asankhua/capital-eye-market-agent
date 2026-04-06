import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, TrendingUp, DollarSign } from 'lucide-react';
import { api } from '../api';
import type { EarningsInfo } from '../types';

export const EarningsCalendar: React.FC = () => {
  const [earnings, setEarnings] = useState<EarningsInfo[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEarnings();
  }, [days]);

  const loadEarnings = async () => {
    setLoading(true);
    try {
      const data = await api.getEarningsCalendar(days);
      setEarnings(data.earnings);
    } catch (error) {
      console.error('Failed to load earnings:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
    });
  };

  const getDaysUntil = (dateStr?: string) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Calendar size={20} color="#f59e0b" />
          <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Earnings Calendar</h3>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(parseInt(e.target.value))}
          style={{
            padding: '6px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border-color)',
            background: 'rgba(255,255,255,0.05)',
            color: 'var(--text-primary)',
            fontSize: '12px',
          }}
        >
          <option value={7}>Next 7 days</option>
          <option value={30}>Next 30 days</option>
          <option value={90}>Next 90 days</option>
        </select>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-secondary)' }}>
          Loading earnings...
        </div>
      ) : earnings.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-secondary)' }}>
          <Calendar size={32} style={{ marginBottom: '8px', opacity: 0.5 }} />
          <p>No upcoming earnings found</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflow: 'auto' }}>
          {earnings.map((item, index) => {
            const daysUntil = getDaysUntil(item.earnings_date);
            return (
              <motion.div
                key={item.ticker}
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
                    <span style={{ fontWeight: 600, fontSize: '14px' }}>{item.ticker}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                      <Calendar size={12} color="var(--text-secondary)" />
                      <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {formatDate(item.earnings_date)}
                      </span>
                      {daysUntil !== null && (
                        <span style={{
                          fontSize: '10px',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          background: daysUntil <= 7 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                          color: daysUntil <= 7 ? '#f59e0b' : '#10b981',
                        }}>
                          {daysUntil === 0 ? 'Today' : `${daysUntil} days`}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '11px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <TrendingUp size={12} color="var(--text-secondary)" />
                    <span style={{ color: 'var(--text-secondary)' }}>EPS Est:</span>
                    <span style={{ fontWeight: 500 }}>₹{item.eps_estimate?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <DollarSign size={12} color="var(--text-secondary)" />
                    <span style={{ color: 'var(--text-secondary)' }}>Rev Est:</span>
                    <span style={{ fontWeight: 500 }}>₹{item.revenue_estimate ? (item.revenue_estimate / 1e9).toFixed(1) + 'B' : 'N/A'}</span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
};
