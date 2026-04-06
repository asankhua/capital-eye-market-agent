import React, { useState } from 'react';
import { Download, FileText, FileSpreadsheet, FileJson, Check } from 'lucide-react';
import { api } from '../api';

export const ExportReports: React.FC = () => {
  const [ticker, setTicker] = useState('');
  const [format, setFormat] = useState<'pdf' | 'csv' | 'json'>('json');
  const [loading, setLoading] = useState(false);
  const [exported, setExported] = useState(false);

  const handleExport = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setExported(false);
    try {
      const blob = await api.exportReport({ ticker: ticker.toUpperCase(), format });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${ticker.toUpperCase()}_analysis.${format === 'json' ? 'json' : format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setExported(true);
      setTimeout(() => setExported(false), 3000);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formats = [
    { id: 'json', label: 'JSON', icon: FileJson, desc: 'Raw data for developers' },
    { id: 'csv', label: 'CSV', icon: FileSpreadsheet, desc: 'Spreadsheet format' },
    { id: 'pdf', label: 'PDF', icon: FileText, desc: 'Professional report' },
  ] as const;

  return (
    <div style={{
      background: 'var(--bg-surface)',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <Download size={20} color="#3b82f6" />
        <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Export Reports</h3>
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>
          Stock Ticker
        </label>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="e.g. RELIANCE.NS"
          style={{
            width: '100%',
            padding: '10px 14px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            background: 'rgba(255,255,255,0.05)',
            color: 'var(--text-primary)',
            fontSize: '14px',
          }}
        />
      </div>

      <div style={{ marginBottom: '16px' }}>
        <label style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'block' }}>
          Export Format
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
          {formats.map((f) => {
            const Icon = f.icon;
            return (
              <button
                key={f.id}
                onClick={() => setFormat(f.id)}
                style={{
                  padding: '12px 8px',
                  borderRadius: '8px',
                  border: `1px solid ${format === f.id ? 'var(--accent-color)' : 'var(--border-color)'}`,
                  background: format === f.id ? 'rgba(59, 130, 246, 0.1)' : 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Icon size={20} color={format === f.id ? '#3b82f6' : 'var(--text-secondary)'} />
                <span style={{ fontSize: '12px', fontWeight: 500 }}>{f.label}</span>
                <span style={{ fontSize: '10px', color: 'var(--text-secondary)' }}>{f.desc}</span>
              </button>
            );
          })}
        </div>
      </div>

      <button
        onClick={handleExport}
        disabled={loading || !ticker.trim()}
        style={{
          width: '100%',
          padding: '12px',
          borderRadius: '8px',
          border: 'none',
          background: exported ? '#10b981' : 'var(--accent-color)',
          color: 'white',
          fontWeight: 500,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          transition: 'all 0.2s',
        }}
      >
        {exported ? <Check size={16} /> : <Download size={16} />}
        {loading ? 'Exporting...' : exported ? 'Downloaded!' : `Export as ${format.toUpperCase()}`}
      </button>
    </div>
  );
};
