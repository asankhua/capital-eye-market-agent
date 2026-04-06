import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Star, Plus, Trash2, TrendingUp } from 'lucide-react';
import { watchlistStorage } from '../watchlist-storage';

export const Watchlist: React.FC = () => {
  const [watchlist, setWatchlist] = useState<{symbol: string, addedAt: number}[]>([]);
  const [newTicker, setNewTicker] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadWatchlist();
  }, []);

  const loadWatchlist = () => {
    try {
      const data = watchlistStorage.getAll();
      setWatchlist(data);
    } catch (error) {
      console.error('Failed to load watchlist:', error);
    }
  };

  const addStock = () => {
    if (!newTicker.trim()) return;
    setLoading(true);
    try {
      watchlistStorage.add(newTicker.toUpperCase());
      setNewTicker('');
      loadWatchlist();
    } catch (error) {
      console.error('Failed to add stock:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeStock = (ticker: string) => {
    try {
      watchlistStorage.remove(ticker);
      loadWatchlist();
    } catch (error) {
      console.error('Failed to remove stock:', error);
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
        <Star size={20} color="#fbbf24" />
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Watchlist</h3>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <input
          type="text"
          value={newTicker}
          onChange={(e) => setNewTicker(e.target.value)}
          placeholder="Add stock (e.g. RELIANCE.NS)"
          style={{
            flex: 1,
            padding: '10px 14px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            background: 'rgba(255,255,255,0.05)',
            color: 'var(--text-primary)',
            fontSize: '14px',
          }}
          onKeyPress={(e) => e.key === 'Enter' && addStock()}
        />
        <button
          onClick={addStock}
          disabled={loading}
          style={{
            padding: '10px 16px',
            borderRadius: '8px',
            border: 'none',
            background: 'var(--accent-color)',
            color: 'white',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <Plus size={16} />
          Add
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {watchlist.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-secondary)' }}>
            <Star size={32} style={{ marginBottom: '8px', opacity: 0.5 }} />
            <p>No stocks in watchlist</p>
            <p style={{ fontSize: '12px', marginTop: '4px' }}>Add stocks to track them easily</p>
          </div>
        ) : (
          watchlist.map((item, index) => (
            <motion.div
              key={item.symbol}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                background: 'rgba(255,255,255,0.03)',
                borderRadius: '10px',
                border: '1px solid var(--border-color)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <TrendingUp size={16} color="var(--accent-color)" />
                <span style={{ fontWeight: 500 }}>{item.symbol}</span>
              </div>
              <button
                onClick={() => removeStock(item.symbol)}
                style={{
                  padding: '6px',
                  borderRadius: '6px',
                  border: 'none',
                  background: 'transparent',
                  color: 'var(--danger)',
                  cursor: 'pointer',
                }}
              >
                <Trash2 size={14} />
              </button>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};
