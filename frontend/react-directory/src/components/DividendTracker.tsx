import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Coins, Calendar, Search, Clock } from 'lucide-react';
import { api } from '../api';

interface DividendAnnouncement {
  symbol: string;
  company_name: string;
  purpose: string;
  dividend_type: string;
  ex_date?: string;
  record_date?: string;
  announcement_date?: string;
  face_value?: string;
  source?: string;
}

export const DividendTracker: React.FC = () => {
  const [dividends, setDividends] = useState<DividendAnnouncement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    loadDividends();
  }, []);

  const loadDividends = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getBSEDividendAnnouncements(30, 30);
      const allDividends = [
        ...(data.recent?.dividends || []),
        ...(data.upcoming?.dividends || [])
      ];
      
      // Remove duplicates based on symbol + record_date
      const uniqueDividends = allDividends.filter((dividend, index, self) =>
        index === self.findIndex((d) => (
          d.symbol === dividend.symbol && d.record_date === dividend.record_date
        ))
      );
      
      if (uniqueDividends.length > 0) {
        setDividends(uniqueDividends);
      } else {
        setDividends([]);
      }
      setLastUpdated(`${new Date().toLocaleString('en-IN', { 
        timeZone: 'Asia/Kolkata',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })} IST (from BSE Corporate Actions)`);
    } catch (err) {
      setError('Failed to load dividend announcements');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const formatTimeAgo = (dateString?: string): string => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 30) return `${diffDays} days ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  const filteredDividends = dividends.filter(d => 
    d.symbol?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.company_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <Coins size={28} color="#10b981" />
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>Dividend Announcements</h2>
        </div>
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <Coins size={48} style={{ margin: '0 auto 16px', opacity: 0.3 }} />
          <p>Loading dividend announcements...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <Coins size={28} color="#10b981" />
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>Dividend Announcements</h2>
        </div>
        <div style={{ padding: '24px', background: '#fee2e2', borderRadius: '12px', color: '#dc2626' }}>
          <p>{error}</p>
          <button 
            onClick={loadDividends}
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
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <Coins size={28} color="#10b981" />
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>Dividend Announcements</h2>
          {lastUpdated && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px', fontSize: '12px', color: '#6b7280' }}>
              <Clock size={12} />
              <span>Last updated: {lastUpdated}</span>
            </div>
          )}
        </div>
        <span style={{
          marginLeft: 'auto',
          fontSize: '14px',
          color: '#6b7280',
          background: '#f3f4f6',
          padding: '6px 12px',
          borderRadius: '20px',
          fontWeight: 500,
        }}>
          {filteredDividends.length} announcements
        </span>
      </div>

      {/* Search Bar */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          background: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
          padding: '0 16px',
          maxWidth: '400px',
        }}>
          <Search size={20} color="#9ca3af" style={{ marginRight: '12px' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by company or ticker..."
            style={{
              flex: 1,
              padding: '12px 0',
              border: 'none',
              background: 'transparent',
              color: '#0f172a',
              fontSize: '14px',
              outline: 'none',
            }}
          />
        </div>
      </div>

      {/* Dividend Grid - Similar to News Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
        {filteredDividends.map((item, index) => (
          <motion.div
            key={`${item.symbol}-${index}`}
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
              gap: '12px',
            }}
          >
            {/* Header Row */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <span style={{ 
                fontSize: '12px', 
                fontWeight: 700,
                color: '#059669',
                background: '#d1fae5',
                padding: '4px 10px',
                borderRadius: '20px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}>
                {item.symbol}
              </span>
              <span style={{ fontSize: '12px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Clock size={12} />
                {formatTimeAgo(item.announcement_date)}
              </span>
            </div>

            {/* Company Name */}
            <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a', lineHeight: 1.4, margin: 0 }}>
              {item.company_name}
            </h3>

            {/* Dividend Details */}
            <div style={{ display: 'flex', gap: '16px', marginTop: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Coins size={16} color="#10b981" />
                <span style={{ fontSize: '14px', fontWeight: 600, color: '#10b981' }}>
                  {item.purpose || 'Dividend'}
                </span>
              </div>
            </div>

            {/* Dates */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginTop: 'auto',
              paddingTop: '12px',
              borderTop: '1px solid #f3f4f6',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Calendar size={14} color="#6b7280" />
                <span style={{ fontSize: '12px', color: '#6b7280' }}>
                  Ex-Date: {formatDate(item.ex_date)}
                </span>
              </div>
              {item.record_date && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '12px', color: '#6b7280' }}>
                    Record: {formatDate(item.record_date)}
                  </span>
                </div>
              )}
            </div>

            {/* Source */}
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <span style={{ fontSize: '11px', color: '#9ca3af', fontWeight: 500 }}>
                Source: {item.source || 'BSE India'}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredDividends.length === 0 && !loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <Coins size={48} style={{ margin: '0 auto 16px', opacity: 0.3 }} />
          <p>No dividend announcements found.</p>
          {searchQuery && <p style={{ fontSize: '14px', marginTop: '8px' }}>Try a different search term</p>}
        </div>
      )}
    </div>
  );
};
