import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Newspaper, ExternalLink, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { debugLogger } from '../debug-logger';
import type { NewsArticle } from '../types';

interface NewsItem {
  id: string;
  title: string;
  source: string;
  publishedAt: string;
  url: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  summary: string;
}

interface NewsSectionProps {
  stock: string;
  news?: NewsArticle[];
}

const getSentimentIcon = (sentiment: string) => {
  switch (sentiment) {
    case 'positive':
      return <TrendingUp size={14} color="#10b981" />;
    case 'negative':
      return <TrendingDown size={14} color="#ef4444" />;
    default:
      return <Minus size={14} color="#6b7280" />;
  }
};

const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case 'positive':
      return '#10b981';
    case 'negative':
      return '#ef4444';
    default:
      return '#6b7280';
  }
};

const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

export const NewsSection: React.FC<NewsSectionProps> = ({ stock, news: propNews }) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    // Convert prop news to NewsItem format
    if (propNews && propNews.length > 0) {
      const formattedNews: NewsItem[] = propNews.map((article, idx) => ({
        id: `${stock}-news-${idx}`,
        title: article.title || article.summary?.substring(0, 60) || 'News article',
        source: article.publisher || 'Yahoo Finance',
        publishedAt: article.publish_time || new Date().toISOString(),
        url: article.link || '#',
        sentiment: 'neutral', // Could analyze sentiment from title
        summary: article.summary || article.title || 'No summary available',
      }));
      setNews(formattedNews);
      debugLogger.logUiEvent('News loaded from props', { stock, count: formattedNews.length });
    } else {
      setNews([]);
    }
  }, [stock, propNews]);

  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        marginBottom: '16px',
        paddingBottom: '12px',
        borderBottom: '1px solid var(--border-color)',
      }}>
        <Newspaper size={20} color="var(--accent-color)" />
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Latest News</h3>
        <span style={{
          marginLeft: 'auto',
          fontSize: '12px',
          color: 'var(--text-secondary)',
          background: 'rgba(255,255,255,0.05)',
          padding: '4px 10px',
          borderRadius: '12px',
        }}>
          {news.length} articles
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {news.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            style={{
              padding: '14px',
              background: 'rgba(255,255,255,0.03)',
              borderRadius: '12px',
              border: '1px solid var(--border-color)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.06)';
              e.currentTarget.style.transform = 'translateX(4px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
              e.currentTarget.style.transform = 'translateX(0)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: `${getSentimentColor(item.sentiment)}20`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}>
                {getSentimentIcon(item.sentiment)}
              </div>
              
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '4px',
                }}>
                  <span style={{
                    fontSize: '11px',
                    color: 'var(--text-secondary)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    fontWeight: 500,
                  }}>
                    {item.source}
                  </span>
                  <span style={{ color: 'var(--border-color)' }}>•</span>
                  <span style={{
                    fontSize: '11px',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    <Clock size={10} />
                    {formatTimeAgo(item.publishedAt)}
                  </span>
                </div>
                
                <h4 style={{
                  fontSize: '14px',
                  fontWeight: 500,
                  lineHeight: 1.4,
                  color: 'var(--text-primary)',
                  marginBottom: expandedId === item.id ? '8px' : 0,
                }}>
                  {item.title}
                </h4>
                
                {expandedId === item.id && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    style={{
                      fontSize: '13px',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.5,
                      marginTop: '8px',
                      paddingTop: '8px',
                      borderTop: '1px solid var(--border-color)',
                    }}
                  >
                    {item.summary}
                  </motion.p>
                )}
              </div>
              
              <ExternalLink size={14} color="var(--text-secondary)" style={{ flexShrink: 0 }} />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
