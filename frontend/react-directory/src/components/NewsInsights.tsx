import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Newspaper, Clock } from 'lucide-react';
import { api } from '../api';

interface NewsItem {
  category: string;
  datetime: number;
  headline: string;
  source: string;
  summary: string;
  url: string;
}

export const NewsInsights: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    loadNews();
  }, []);

  const loadNews = async () => {
    setLoading(true);
    try {
      // Load Indian market news
      const categoryData = await api.getIndianMarketNews(10);
      setNews(categoryData.news || []);
      setLastUpdated(`${new Date().toLocaleString('en-IN', { 
        timeZone: 'Asia/Kolkata',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })} IST (from NewsData.io)`);
    } catch (err) {
      setError('Failed to load news');
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
          <p>Loading news...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px', background: '#fee2e2', borderRadius: '12px', color: '#dc2626' }}>
        <p>{error}</p>
        <button 
          onClick={loadNews}
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
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>News & Insights</h2>
          {lastUpdated && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px', fontSize: '12px', color: '#6b7280' }}>
              <Clock size={12} />
              <span>Last updated: {lastUpdated}</span>
            </div>
          )}
        </div>
      </div>

      {/* News Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', 
        gap: '16px',
        maxWidth: '100%',
        overflowX: 'hidden'
      }}>
        {news.map((item, index) => (
          <motion.div
            key={index}
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
              flexDirection: 'column',
              gap: '8px',
              maxWidth: '100%',
              overflow: 'hidden'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
                <Clock size={12} />
                {new Date(item.datetime * 1000).toLocaleString('en-US', { 
                  month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
                })}
              </span>
            </div>
            
            <h3 style={{ 
              fontSize: '16px', 
              fontWeight: 600, 
              color: '#0f172a', 
              lineHeight: 1.4,
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
              maxWidth: '100%'
            }}>
              <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: '#0f172a', textDecoration: 'none' }}>
                {item.headline}
              </a>
            </h3>
            
            <p style={{ 
              fontSize: '14px', 
              color: '#4b5563', 
              lineHeight: 1.5,
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
              maxWidth: '100%'
            }}>
              {item.summary}
            </p>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '8px' }}>
              <span style={{ fontSize: '12px', color: '#6b7280', fontWeight: 600, wordBreak: 'break-word' }}>
                Source: {item.source}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {news.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <Newspaper size={48} style={{ margin: '0 auto 16px', opacity: 0.3 }} />
          <p>No news available at the moment. Please try again later.</p>
          {error && <p style={{ fontSize: '12px', marginTop: '8px', color: '#ef4444' }}>{error}</p>}
        </div>
      )}
    </div>
  );
};
