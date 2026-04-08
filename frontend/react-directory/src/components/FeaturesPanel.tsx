import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Star, Coins, X, ChevronRight 
} from 'lucide-react';
import { Watchlist } from './Watchlist';
import { DividendTracker } from './DividendTracker';

const features = [
  { id: 'watchlist', label: 'Watchlist', icon: Star, color: '#fbbf24', component: Watchlist },
  { id: 'dividend', label: 'Dividends', icon: Coins, color: '#10b981', component: DividendTracker },
];

export const FeaturesPanel: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeFeature, setActiveFeature] = useState<string | null>(null);

  const activeComponent = activeFeature 
    ? features.find(f => f.id === activeFeature)?.component 
    : null;

  return (
    <>
      {/* Floating Features Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.05 }}
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          right: '20px',
          top: '80px',
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          border: 'none',
          background: 'var(--accent-color)',
          color: 'white',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 100,
        }}
        title="Advanced Features"
      >
        <Star size={20} />
      </motion.button>

      {/* Features Drawer */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0,0,0,0.5)',
                zIndex: 200,
              }}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              style={{
                position: 'fixed',
                right: 0,
                top: 0,
                bottom: 0,
                width: '400px',
                maxWidth: '90vw',
                background: 'var(--bg-primary)',
                borderLeft: '1px solid var(--border-color)',
                zIndex: 201,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* Header */}
              <div style={{
                padding: '20px',
                borderBottom: '1px solid var(--border-color)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <h2 style={{ fontSize: '18px', fontWeight: 600 }}>Advanced Features</h2>
                <button
                  onClick={() => {
                    setIsOpen(false);
                    setActiveFeature(null);
                  }}
                  style={{
                    padding: '8px',
                    borderRadius: '8px',
                    border: 'none',
                    background: 'transparent',
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                  }}
                >
                  <X size={20} />
                </button>
              </div>

              {/* Content */}
              <div style={{
                flex: 1,
                overflow: 'auto',
                padding: '20px',
              }}>
                {activeFeature ? (
                  <div>
                    <button
                      onClick={() => setActiveFeature(null)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        marginBottom: '16px',
                        padding: '8px',
                        border: 'none',
                        background: 'transparent',
                        color: 'var(--accent-color)',
                        cursor: 'pointer',
                        fontSize: '14px',
                      }}
                    >
                      <ChevronRight size={16} style={{ transform: 'rotate(180deg)' }} />
                      Back to features
                    </button>
                    {activeComponent && React.createElement(activeComponent)}
                  </div>
                ) : (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '12px',
                  }}>
                    {features.map((feature, index) => {
                      const Icon = feature.icon;
                      return (
                        <motion.button
                          key={feature.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          onClick={() => setActiveFeature(feature.id)}
                          style={{
                            padding: '20px',
                            borderRadius: '12px',
                            border: `1px solid ${feature.color}30`,
                            background: `${feature.color}10`,
                            cursor: 'pointer',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: '10px',
                            transition: 'all 0.2s',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = `${feature.color}20`;
                            e.currentTarget.style.transform = 'translateY(-2px)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = `${feature.color}10`;
                            e.currentTarget.style.transform = 'translateY(0)';
                          }}
                        >
                          <Icon size={24} color={feature.color} />
                          <span style={{
                            fontSize: '13px',
                            fontWeight: 500,
                            color: feature.color,
                            textAlign: 'center',
                          }}>
                            {feature.label}
                          </span>
                        </motion.button>
                      );
                    })}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};
