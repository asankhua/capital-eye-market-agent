import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity, DollarSign, PieChart, Newspaper } from 'lucide-react';
import type { StockAnalysis } from '../types';
import { NewsSection } from './NewsSection';

interface StockCardProps {
  data: StockAnalysis;
}

export const StockCard: React.FC<StockCardProps> = ({ data }) => {
  const getScoreColor = (score: number) => {
    if (score >= 7) return '#059669';
    if (score >= 4) return '#d97706';
    return '#dc2626';
  };

  const getScoreBg = (score: number) => {
    if (score >= 7) return '#d1fae5';
    if (score >= 4) return '#fef3c7';
    return '#fee2e2';
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ 
        background: '#ffffff',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div style={{ 
        padding: '20px 24px',
        borderBottom: '1px solid #e2e8f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: '#f8fafc',
      }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            {data.stock}
          </h2>
          <p style={{ fontSize: '13px', color: '#64748b' }}>Last updated: Just now</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[
            { label: 'Fundamental', score: data.fundamental.score },
            { label: 'Technical', score: data.technical.score },
            { label: 'Sentiment', score: data.sentiment.score },
          ].map((item) => (
            <div key={item.label} style={{
              padding: '8px 12px',
              borderRadius: '8px',
              background: getScoreBg(item.score),
              border: `1px solid ${getScoreColor(item.score)}20`,
            }}>
              <p style={{ fontSize: '10px', color: '#64748b', textTransform: 'uppercase', fontWeight: 600, marginBottom: '2px' }}>
                {item.label}
              </p>
              <p style={{ fontSize: '16px', fontWeight: 700, color: getScoreColor(item.score) }}>
                {item.score}/10
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Scrollable Content - All Sections */}
      <div style={{ padding: '24px', overflowY: 'auto', maxHeight: 'calc(100vh - 250px)' }}>
        {/* Overview Section */}
        <section style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <PieChart size={20} color="#1e40af" />
            <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a' }}>Overview</h3>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
            {/* Fundamental Card */}
            <div style={{
              padding: '16px',
              borderRadius: '10px',
              border: '1px solid #e2e8f0',
              background: '#f8fafc',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <DollarSign size={18} color="#1e40af" />
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>Fundamental</h3>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '13px' }}>
                <div style={{ padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                  <span style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>P/E</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{data.fundamental.pe_ratio || 'N/A'}</span>
                </div>
                <div style={{ padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                  <span style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>Margin</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{data.fundamental.profit_margin}</span>
                </div>
                <div style={{ padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                  <span style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>Growth</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{data.fundamental.earnings_growth}</span>
                </div>
                <div style={{ padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                  <span style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>Debt</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{data.fundamental.debt}</span>
                </div>
              </div>
              <p style={{ marginTop: '12px', fontSize: '12px', lineHeight: 1.5, color: '#475569' }}>
                {data.fundamental.summary}
              </p>
            </div>

            {/* Technical Card */}
            <div style={{
              padding: '16px',
              borderRadius: '10px',
              border: '1px solid #e2e8f0',
              background: '#f8fafc',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <Activity size={18} color="#1e40af" />
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>Technical</h3>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '13px' }}>
                <div style={{ padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                  <span style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>RSI</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{data.technical.rsi !== undefined ? data.technical.rsi : 'N/A'}</span>
                </div>
                <div style={{ padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                  <span style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>Trend</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{data.technical.trend}</span>
                </div>
                <div style={{ padding: '8px', background: '#ffffff', borderRadius: '6px', gridColumn: 'span 2' }}>
                  <span style={{ color: '#64748b', display: 'block', marginBottom: '2px' }}>MACD</span>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{data.technical.macd}</span>
                </div>
              </div>
              <p style={{ marginTop: '12px', fontSize: '12px', lineHeight: 1.5, color: '#475569' }}>
                {data.technical.summary}
              </p>
            </div>

            {/* Sentiment Card */}
            <div style={{
              padding: '16px',
              borderRadius: '10px',
              border: '1px solid #e2e8f0',
              background: '#f8fafc',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <PieChart size={18} color="#1e40af" />
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>Sentiment</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {(data.sentiment.positive_signals?.length || 0) > 0 ? (
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                    <TrendingUp size={16} color="#059669" />
                    <div>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>Positive</span>
                      <span style={{ fontSize: '12px', color: '#0f172a', display: 'block' }}>{data.sentiment.positive_signals.slice(0, 2).join(', ')}</span>
                    </div>
                  </div>
                ) : null}
                {(data.sentiment.negative_signals?.length || 0) > 0 ? (
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', padding: '8px', background: '#ffffff', borderRadius: '6px' }}>
                    <TrendingDown size={16} color="#dc2626" />
                    <div>
                      <span style={{ fontSize: '11px', color: '#64748b' }}>Negative</span>
                      <span style={{ fontSize: '12px', color: '#0f172a', display: 'block' }}>{data.sentiment.negative_signals.slice(0, 2).join(', ')}</span>
                    </div>
                  </div>
                ) : null}
              </div>
              <p style={{ marginTop: '12px', fontSize: '12px', lineHeight: 1.5, color: '#475569' }}>
                {data.sentiment.summary}
              </p>
            </div>
          </div>
        </section>

        {/* News Section */}
        <section>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Newspaper size={20} color="#1e40af" />
            <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a' }}>News</h3>
          </div>
          <div style={{ padding: '16px', background: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
            <NewsSection stock={data.stock} news={data.news} />
          </div>
        </section>
      </div>
    </motion.div>
  );
};
