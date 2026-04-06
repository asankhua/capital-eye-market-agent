import React from 'react';
import { 
  LayoutDashboard, 
  TrendingUp,
  Newspaper, 
  PieChart,
  ChevronRight,
  Globe,
  Coins,
  Menu,
} from 'lucide-react';

const mainNavItems = [
  { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { id: 'dividends', icon: Coins, label: 'Dividend' },
];

const marketNavItems = [
  { id: 'market-overview', icon: Globe, label: 'Market Overview' },
  { id: 'market-movers', icon: TrendingUp, label: 'Market Movers' },
  { id: 'news', icon: Newspaper, label: 'News & Insights' },
  { id: 'sector', icon: PieChart, label: 'Sector Analysis' },
];

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onViewChange }) => {
  const isActive = (id: string) => activeView === id;
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  // Close mobile menu when view changes
  const handleViewChange = (view: string) => {
    onViewChange(view);
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      {/* Mobile Menu Toggle Button */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        style={{
          position: 'fixed',
          top: '72px',
          left: '12px',
          zIndex: 60,
          padding: '10px',
          borderRadius: '8px',
          border: 'none',
          background: '#ffffff',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          cursor: 'pointer',
          display: window.innerWidth <= 768 ? 'flex' : 'none',
        }}
      >
        <Menu size={20} color="#64748b" />
      </button>

      <aside style={{
        width: '260px',
        background: '#ffffff',
        borderRight: '1px solid #e2e8f0',
        height: 'calc(100vh - 60px)',
        position: 'fixed',
        left: window.innerWidth <= 768 ? (isMobileMenuOpen ? 0 : '-260px') : 0,
        top: '60px',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 50,
        overflow: 'hidden',
        transition: 'left 0.3s ease',
      }}>
      <nav style={{ padding: '16px', flex: 1, overflow: 'auto' }}>
        {/* Analysis Section */}
        <div style={{ marginBottom: '8px' }}>
          <p style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#94a3b8',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '8px',
            paddingLeft: '12px',
          }}>
            Analysis
          </p>
          
          {mainNavItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.id);
            return (
              <button
                key={item.id}
                onClick={() => handleViewChange(item.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  background: active ? '#eff6ff' : 'transparent',
                  color: active ? '#1e40af' : '#64748b',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 500,
                  marginBottom: '2px',
                  transition: 'all 0.2s',
                }}
              >
                <Icon size={18} />
                <span style={{ flex: 1, textAlign: 'left' }}>{item.label}</span>
                {active && <ChevronRight size={16} />}
              </button>
            );
          })}
        </div>

        <div style={{ height: '1px', background: '#e2e8f0', margin: '16px 0' }} />

        {/* Market Intelligence Section */}
        <div style={{ marginBottom: '8px' }}>
          <p style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#94a3b8',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '8px',
            paddingLeft: '12px',
          }}>
            Market Intelligence
          </p>
          
          {marketNavItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.id);
            return (
              <button
                key={item.id}
                onClick={() => handleViewChange(item.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: 'none',
                  background: active ? '#eff6ff' : 'transparent',
                  color: active ? '#1e40af' : '#64748b',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 500,
                  marginBottom: '2px',
                  transition: 'all 0.2s',
                }}
              >
                <Icon size={18} />
                <span style={{ flex: 1, textAlign: 'left' }}>{item.label}</span>
              </button>
            );
          })}
        </div>

        <div style={{ height: '1px', background: '#e2e8f0', margin: '16px 0' }} />

        {/* Quick Tips Section */}
        <div style={{ marginBottom: '8px' }}>
          <p style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#94a3b8',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '8px',
            paddingLeft: '12px',
          }}>
            Quick Tips
          </p>
          <div style={{ 
            padding: '12px', 
            background: '#f8fafc', 
            borderRadius: '8px',
            marginLeft: '12px',
            marginRight: '12px',
          }}>
            <ul style={{ 
              fontSize: '12px', 
              color: '#64748b', 
              lineHeight: '1.6',
              margin: 0,
              paddingLeft: '16px',
            }}>
              <li>Search stocks like "RELIANCE" or "TCS"</li>
              <li>Ask "Compare RELIANCE vs TCS"</li>
              <li>Use Dividend Tracker for payouts</li>
              <li>Check Market Movers for trends</li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Bottom Section */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid #e2e8f0',
        background: '#f8fafc',
      }}>
        <div style={{ fontSize: '12px', color: '#94a3b8', textAlign: 'center' }}>
          Capital Eye
        </div>
      </div>
    </aside>
    </>
  );
};
