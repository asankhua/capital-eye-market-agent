import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { Sidebar } from './components/Sidebar';
import { ChatPanel } from './components/ChatPanel';
import { MarketOverview } from './components/MarketOverview';
import { MarketMovers } from './components/MarketMovers';
import { NewsInsights } from './components/NewsInsights';
import { SectorAnalysis } from './components/SectorAnalysis';
import { DividendTracker } from './components/DividendTracker';
import { SettingsPage } from './components/SettingsPage';

const STORAGE_KEY = 'capitaleye_settings';

function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Load theme from localStorage
  useEffect(() => {
    const loadTheme = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          const theme = parsed.theme || 'light';
          
          if (theme === 'dark') {
            setIsDarkMode(true);
            document.body.classList.add('dark-mode');
          } else if (theme === 'system') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            setIsDarkMode(prefersDark);
            if (prefersDark) {
              document.body.classList.add('dark-mode');
            }
          } else {
            setIsDarkMode(false);
            document.body.classList.remove('dark-mode');
          }
        }
      } catch (error) {
        console.error('Error loading theme:', error);
      }
    };
    
    loadTheme();
    
    // Listen for settings changes
    const handleSettingsChange = (event: CustomEvent) => {
      const theme = event.detail?.theme || 'light';
      
      if (theme === 'dark') {
        setIsDarkMode(true);
        document.body.classList.add('dark-mode');
      } else if (theme === 'system') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setIsDarkMode(prefersDark);
        if (prefersDark) {
          document.body.classList.add('dark-mode');
        } else {
          document.body.classList.remove('dark-mode');
        }
      } else {
        setIsDarkMode(false);
        document.body.classList.remove('dark-mode');
      }
    };
    
    window.addEventListener('settingsUpdated', handleSettingsChange as EventListener);
    
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed.theme === 'system') {
          setIsDarkMode(e.matches);
          if (e.matches) {
            document.body.classList.add('dark-mode');
          } else {
            document.body.classList.remove('dark-mode');
          }
        }
      }
    };
    
    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    return () => {
      window.removeEventListener('settingsUpdated', handleSettingsChange as EventListener);
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const renderContent = () => {
    switch (activeView) {
      case 'dashboard':
        return <ChatPanel />;
      case 'market-overview':
        return <MarketOverview />;
      case 'market-movers':
        return <MarketMovers />;
      case 'news':
        return <NewsInsights />;
      case 'sector':
        return <SectorAnalysis />;
      case 'dividends':
        return <DividendTracker />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <ChatPanel />;
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: '100vh', 
      width: '100vw', 
      background: '#f8fafc',
      overflow: 'hidden' 
    }}>
      <Header onSettingsClick={() => setActiveView('settings')} />
      
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar activeView={activeView} onViewChange={setActiveView} />

        <main style={{ 
          flex: 1, 
          marginLeft: isMobile ? '0' : '260px',
          marginTop: '60px',
          padding: isMobile ? '16px' : '24px',
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {renderContent()}
        </main>
      </div>
      <Footer />
    </div>
  );
}

export default App;
