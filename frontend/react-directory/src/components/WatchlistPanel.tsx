import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, X, Plus, Trash2, TrendingUp } from 'lucide-react';
import { watchlistStorage, type WatchlistItem } from '../watchlist-storage';
import { debugLogger } from '../debug-logger';

interface WatchlistPanelProps {
  onSelectStock: (symbol: string) => void;
}

export const WatchlistPanel: React.FC<WatchlistPanelProps> = ({ onSelectStock }) => {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');

  useEffect(() => {
    refreshItems();
  }, []);

  const refreshItems = () => {
    setItems(watchlistStorage.getAll());
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol.trim()) return;
    
    const symbol = newSymbol.trim().toUpperCase();
    if (watchlistStorage.add(symbol)) {
      refreshItems();
      setNewSymbol('');
    }
  };

  const handleRemove = (symbol: string) => {
    watchlistStorage.remove(symbol);
    refreshItems();
  };

  const handleSelect = (symbol: string) => {
    onSelectStock(symbol);
    setIsOpen(false);
    debugLogger.logUiEvent('Selected stock from watchlist', { symbol });
  };

  return (
    <>
      {/* Floating Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          top: '140px',
          right: '20px',
          width: '44px',
          height: '44px',
          borderRadius: '50%',
          background: items.length > 0 ? 'var(--accent-color)' : 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          backdropFilter: 'blur(10px)',
          zIndex: 998,
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        }}
        title="Watchlist"
      >
        <Star size={20} fill={items.length > 0 ? 'currentColor' : 'none'} />
        {items.length > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              background: 'var(--danger)',
              fontSize: '11px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {items.length}
          </span>
        )}
      </motion.button>

      {/* Watchlist Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, x: 300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 300 }}
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              width: '320px',
              height: '100vh',
              background: 'var(--bg-color)',
              borderLeft: '1px solid var(--border-color)',
              zIndex: 997,
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '-4px 0 20px rgba(0,0,0,0.3)',
            }}
          >
            {/* Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '20px',
                borderBottom: '1px solid var(--border-color)',
              }}
            >
              <h3 style={{ fontSize: '18px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Star size={20} fill="var(--accent-color)" color="var(--accent-color)" />
                Watchlist
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-secondary)',
                  padding: '4px',
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Add Stock Form */}
            <form
              onSubmit={handleAdd}
              style={{
                padding: '16px 20px',
                borderBottom: '1px solid var(--border-color)',
                display: 'flex',
                gap: '8px',
              }}
            >
              <input
                type="text"
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value)}
                placeholder="Add symbol (e.g., RELIANCE)"
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)',
                  fontSize: '14px',
                  outline: 'none',
                }}
              />
              <button
                type="submit"
                disabled={!newSymbol.trim()}
                style={{
                  padding: '10px',
                  background: newSymbol.trim() ? 'var(--accent-color)' : 'var(--bg-surface)',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: newSymbol.trim() ? 'pointer' : 'not-allowed',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Plus size={18} />
              </button>
            </form>

            {/* Stock List */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '12px' }}>
              {items.length === 0 ? (
                <div
                  style={{
                    textAlign: 'center',
                    padding: '40px 20px',
                    color: 'var(--text-secondary)',
                    fontSize: '14px',
                  }}
                >
                  <Star size={40} style={{ marginBottom: '12px', opacity: 0.3 }} />
                  <p>Your watchlist is empty</p>
                  <p style={{ fontSize: '12px', marginTop: '8px' }}>
                    Add stocks to track them quickly
                  </p>
                </div>
              ) : (
                items.map((item) => (
                  <motion.div
                    key={item.symbol}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '12px',
                      background: 'var(--bg-surface)',
                      borderRadius: '10px',
                      marginBottom: '8px',
                      border: '1px solid var(--border-color)',
                    }}
                  >
                    <button
                      onClick={() => handleSelect(item.symbol)}
                      style={{
                        flex: 1,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        textAlign: 'left',
                        color: 'var(--text-primary)',
                      }}
                    >
                      <TrendingUp size={16} color="var(--accent-color)" />
                      <span style={{ fontWeight: 600, fontSize: '15px' }}>{item.symbol}</span>
                    </button>
                    <button
                      onClick={() => handleRemove(item.symbol)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        color: 'var(--danger)',
                        padding: '4px',
                        opacity: 0.7,
                      }}
                      title="Remove from watchlist"
                    >
                      <Trash2 size={16} />
                    </button>
                  </motion.div>
                ))
              )}
            </div>

            {/* Footer */}
            {items.length > 0 && (
              <div
                style={{
                  padding: '12px 20px',
                  borderTop: '1px solid var(--border-color)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  {items.length} stock{items.length !== 1 ? 's' : ''}
                </span>
                <button
                  onClick={() => {
                    watchlistStorage.clear();
                    refreshItems();
                  }}
                  style={{
                    fontSize: '12px',
                    color: 'var(--danger)',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  Clear all
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Backdrop */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            zIndex: 996,
          }}
        />
      )}
    </>
  );
};
