import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PieChart, TrendingUp, TrendingDown, Building2, Clock } from 'lucide-react';
import { api } from '../api';

interface Sector {
  sector: string;
  change_percent: number;
}

export const SectorAnalysis: React.FC = () => {
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    loadSectors();
  }, []);

  const loadSectors = async () => {
    setLoading(true);
    try {
      const data = await api.getNSESectorPerformance();
      // Map NSE sector names to match interface
      const mappedSectors = (data.sectors || []).map((s: any) => ({
        sector: s.name || s.sector,
        change_percent: s.change_percent
      }));
      setSectors(mappedSectors);
      setLastUpdated(`${new Date().toLocaleString('en-IN', { 
        timeZone: 'Asia/Kolkata',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })} IST (from ${data.source || 'NSE'})`);
    } catch (err) {
      setError('Failed to load sector performance');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSectorColor = (change: number) => {
    if (change > 2) return '#059669';
    if (change > 0) return '#10b981';
    if (change > -2) return '#f59e0b';
    return '#dc2626';
  };

  const getSectorBg = (change: number) => {
    if (change > 2) return '#d1fae5';
    if (change > 0) return '#ecfdf5';
    if (change > -2) return '#fef3c7';
    return '#fee2e2';
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <div style={{ textAlign: 'center', color: '#64748b' }}>
          <PieChart size={32} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
          <p>Loading sector analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '24px', background: '#fee2e2', borderRadius: '12px', color: '#dc2626' }}>
        <p>{error}</p>
        <button 
          onClick={loadSectors}
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
        <PieChart size={28} color="#2563eb" />
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>Sector Analysis</h2>
          {lastUpdated && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px', fontSize: '12px', color: '#6b7280' }}>
              <Clock size={12} />
              <span>Last updated: {lastUpdated}</span>
            </div>
          )}
        </div>
      </div>

      {/* Market Summary */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '16px',
        marginBottom: '32px' 
      }}>
        <div style={{
          padding: '16px',
          background: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Top Performing Sector</p>
          <p style={{ fontSize: '18px', fontWeight: 700, color: '#059669' }}>
            {sectors.length > 0 ? sectors[0].sector : 'N/A'}
          </p>
          <p style={{ fontSize: '14px', color: '#059669' }}>
            +{sectors.length > 0 ? sectors[0].change_percent.toFixed(2) : 0}%
          </p>
        </div>

        <div style={{
          padding: '16px',
          background: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Worst Performing Sector</p>
          <p style={{ fontSize: '18px', fontWeight: 700, color: '#dc2626' }}>
            {sectors.length > 0 ? sectors[sectors.length - 1].sector : 'N/A'}
          </p>
          <p style={{ fontSize: '14px', color: '#dc2626' }}>
            {sectors.length > 0 ? sectors[sectors.length - 1].change_percent.toFixed(2) : 0}%
          </p>
        </div>

        <div style={{
          padding: '16px',
          background: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Total Sectors</p>
          <p style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a' }}>{sectors.length}</p>
          <p style={{ fontSize: '14px', color: '#6b7280' }}>Tracked</p>
        </div>
      </div>

      {/* Sector Performance Bars */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#374151', marginBottom: '8px' }}>
          Sector Performance Ranking
        </h3>
        
        {sectors.map((sector, index) => (
          <motion.div
            key={sector.sector}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              padding: '12px 16px',
              background: '#ffffff',
              borderRadius: '10px',
              border: '1px solid #e5e7eb',
            }}
          >
            <span style={{ 
              fontSize: '14px', 
              fontWeight: 700, 
              color: '#6b7280',
              width: '30px'
            }}>
              #{index + 1}
            </span>

            <Building2 size={20} color={getSectorColor(sector.change_percent)} />

            <div style={{ flex: 1 }}>
              <p style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a' }}>
                {sector.sector}
              </p>
            </div>

            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              padding: '6px 12px',
              borderRadius: '20px',
              background: getSectorBg(sector.change_percent)
            }}>
              {sector.change_percent >= 0 ? (
                <TrendingUp size={16} color={getSectorColor(sector.change_percent)} />
              ) : (
                <TrendingDown size={16} color={getSectorColor(sector.change_percent)} />
              )}
              <span style={{ 
                fontSize: '14px', 
                fontWeight: 700,
                color: getSectorColor(sector.change_percent)
              }}>
                {sector.change_percent >= 0 ? '+' : ''}{sector.change_percent.toFixed(2)}%
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {sectors.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <PieChart size={48} style={{ margin: '0 auto 16px', opacity: 0.3 }} />
          <p>No sector data available. Please check your API key configuration.</p>
        </div>
      )}
    </div>
  );
};
