import React, { useState, useEffect } from 'react';
import { Settings, Bell, Shield, Database, Save, Check, Trash2, RefreshCw } from 'lucide-react';

interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  notifications: boolean;
  emailAlerts: boolean;
  defaultExchange: string;
  currency: string;
  language: string;
  autoRefresh: boolean;
  refreshInterval: number;
  privacy: {
    shareAnalytics: boolean;
    saveHistory: boolean;
  };
}

const defaultSettings: AppSettings = {
  theme: 'light',
  notifications: false,
  emailAlerts: false,
  defaultExchange: 'NSE',
  currency: 'INR',
  language: 'en',
  autoRefresh: false,
  refreshInterval: 5,
  privacy: {
    shareAnalytics: false,
    saveHistory: true,
  },
};

const STORAGE_KEY = 'capitaleye_settings';

const settingSections = [
  { id: 'general', title: 'General', icon: Settings, description: 'App preferences and defaults' },
  { id: 'notifications', title: 'Notifications', icon: Bell, description: 'Alert settings and frequency' },
  { id: 'security', title: 'Security', icon: Shield, description: 'Privacy and security settings' },
  { id: 'data', title: 'Data Management', icon: Database, description: 'Cache and storage settings' },
];

export const SettingsPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('general');
  const [saved, setSaved] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setSettings({ ...defaultSettings, ...parsed });
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (settings.theme === 'dark') {
      root.style.setProperty('--bg-color', '#0f172a');
      root.style.setProperty('--text-color', '#f8fafc');
      document.body.style.backgroundColor = '#0f172a';
      document.body.style.color = '#f8fafc';
    } else {
      root.style.setProperty('--bg-color', '#f8fafc');
      root.style.setProperty('--text-color', '#0f172a');
      document.body.style.backgroundColor = '#f8fafc';
      document.body.style.color = '#0f172a';
    }
  }, [settings.theme]);

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        updateSetting('notifications', true);
      } else {
        updateSetting('notifications', false);
        alert('Notification permission denied. Please enable in browser settings.');
      }
    }
  };

  const sendTestNotification = () => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('CapitalEye Test', { body: 'Notifications are working!', icon: '/favicon.svg' });
    }
  };

  const clearAllCaches = () => {
    if (confirm('This will clear all cached data. Continue?')) {
      localStorage.removeItem('capitaleye_analysis_cache');
      sessionStorage.clear();
      alert('All caches cleared successfully!');
    }
  };

  const updateSetting = (key: keyof AppSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const updateNestedSetting = (parent: keyof AppSettings, key: string, value: any) => {
    setSettings(prev => ({ ...prev, [parent]: { ...prev[parent] as object, [key]: value } }));
    setHasChanges(true);
  };

  const handleSave = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
      setSaved(true);
      setHasChanges(false);
      setTimeout(() => setSaved(false), 2000);
      window.dispatchEvent(new CustomEvent('settingsUpdated', { detail: settings }));
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings');
    }
  };

  const exportSettings = () => {
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'capitaleye-settings.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const importSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target?.result as string);
        setSettings({ ...defaultSettings, ...imported });
        setHasChanges(true);
        alert('Settings imported! Click Save to apply.');
      } catch (error) {
        alert('Invalid settings file');
      }
    };
    reader.readAsText(file);
  };

  const resetToDefaults = () => {
    if (confirm('Reset all settings to defaults?')) {
      setSettings(defaultSettings);
      setHasChanges(true);
    }
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'general':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>General Settings</h3>
            <div style={{ display: 'grid', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>Default Exchange</label>
                <select value={settings.defaultExchange} onChange={(e) => updateSetting('defaultExchange', e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', background: '#ffffff', fontSize: '14px' }}>
                  <option value="NSE">NSE (India)</option>
                  <option value="BSE">BSE (India)</option>
                  <option value="NASDAQ">NASDAQ (US)</option>
                  <option value="NYSE">NYSE (US)</option>
                </select>
                <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>Default exchange for stock searches</p>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>Currency</label>
                <select value={settings.currency} onChange={(e) => updateSetting('currency', e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', background: '#ffffff', fontSize: '14px' }}>
                  <option value="INR">INR (Indian Rupee)</option>
                  <option value="USD">USD (US Dollar)</option>
                  <option value="EUR">EUR (Euro)</option>
                </select>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#0f172a' }}>Auto-refresh Data</label>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Automatically refresh stock prices every {settings.refreshInterval} minutes</span>
                </div>
                <button onClick={() => updateSetting('autoRefresh', !settings.autoRefresh)} style={{ width: '48px', height: '24px', borderRadius: '12px', border: 'none', background: settings.autoRefresh ? '#2563eb' : '#cbd5e1', position: 'relative', cursor: 'pointer' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#ffffff', position: 'absolute', top: '2px', left: settings.autoRefresh ? '26px' : '2px', transition: 'left 0.2s' }} />
                </button>
              </div>
              {settings.autoRefresh && (
                <div>
                  <label style={{ display: 'block', fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>Refresh Interval (minutes)</label>
                  <input type="number" value={settings.refreshInterval} onChange={(e) => updateSetting('refreshInterval', parseInt(e.target.value) || 5)} min={1} max={60} style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '14px' }} />
                </div>
              )}
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>Notification Settings</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#0f172a' }}>Browser Notifications</label>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Receive alerts about price movements</span>
                </div>
                <button onClick={requestNotificationPermission} style={{ width: '48px', height: '24px', borderRadius: '12px', border: 'none', background: settings.notifications ? '#2563eb' : '#cbd5e1', position: 'relative', cursor: 'pointer' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#ffffff', position: 'absolute', top: '2px', left: settings.notifications ? '26px' : '2px' }} />
                </button>
              </div>
              {settings.notifications && (
                <button onClick={sendTestNotification} style={{ padding: '8px 16px', background: '#eff6ff', color: '#2563eb', border: '1px solid #bfdbfe', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', alignSelf: 'flex-start' }}>
                  Send Test Notification
                </button>
              )}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#0f172a' }}>Email Alerts</label>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Get daily market summary emails</span>
                </div>
                <button onClick={() => updateSetting('emailAlerts', !settings.emailAlerts)} style={{ width: '48px', height: '24px', borderRadius: '12px', border: 'none', background: settings.emailAlerts ? '#2563eb' : '#cbd5e1', position: 'relative', cursor: 'pointer' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#ffffff', position: 'absolute', top: '2px', left: settings.emailAlerts ? '26px' : '2px' }} />
                </button>
              </div>
            </div>
          </div>
        );

      case 'security':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>Privacy & Security</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#0f172a' }}>Save Search History</label>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Store your recent stock searches locally</span>
                </div>
                <button onClick={() => updateNestedSetting('privacy', 'saveHistory', !settings.privacy.saveHistory)} style={{ width: '48px', height: '24px', borderRadius: '12px', border: 'none', background: settings.privacy.saveHistory ? '#2563eb' : '#cbd5e1', position: 'relative', cursor: 'pointer' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#ffffff', position: 'absolute', top: '2px', left: settings.privacy.saveHistory ? '26px' : '2px' }} />
                </button>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#0f172a' }}>Share Anonymous Analytics</label>
                  <span style={{ fontSize: '13px', color: '#64748b' }}>Help improve CapitalEye with usage data</span>
                </div>
                <button onClick={() => updateNestedSetting('privacy', 'shareAnalytics', !settings.privacy.shareAnalytics)} style={{ width: '48px', height: '24px', borderRadius: '12px', border: 'none', background: settings.privacy.shareAnalytics ? '#2563eb' : '#cbd5e1', position: 'relative', cursor: 'pointer' }}>
                  <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#ffffff', position: 'absolute', top: '2px', left: settings.privacy.shareAnalytics ? '26px' : '2px' }} />
                </button>
              </div>
            </div>
          </div>
        );

      case 'data':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>Data Management</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ padding: '16px', background: '#fef2f2', borderRadius: '8px', border: '1px solid #fecaca' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <Trash2 size={20} color="#dc2626" />
                  <span style={{ fontSize: '14px', fontWeight: 600, color: '#dc2626' }}>Clear All Cached Data</span>
                </div>
                <p style={{ fontSize: '13px', color: '#7f1d1d', marginBottom: '12px' }}>This will remove analysis history and temporary storage.</p>
                <button onClick={clearAllCaches} style={{ padding: '8px 16px', background: '#dc2626', color: '#ffffff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Trash2 size={16} /> Clear Cache
                </button>
              </div>
              <div style={{ padding: '16px', background: '#f0fdf4', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  <RefreshCw size={20} color="#16a34a" />
                  <span style={{ fontSize: '14px', fontWeight: 600, color: '#16a34a' }}>Backup & Restore</span>
                </div>
                <p style={{ fontSize: '13px', color: '#14532d', marginBottom: '12px' }}>Export or import your settings configuration.</p>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button onClick={exportSettings} style={{ padding: '8px 16px', background: '#16a34a', color: '#ffffff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' }}>Export Settings</button>
                  <label style={{ padding: '8px 16px', background: '#ffffff', color: '#16a34a', border: '1px solid #16a34a', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' }}>
                    <input type="file" accept=".json" onChange={importSettings} style={{ display: 'none' }} />
                    Import Settings
                  </label>
                </div>
              </div>
              <button onClick={resetToDefaults} style={{ padding: '12px', background: '#f8fafc', color: '#64748b', border: '1px solid #e2e8f0', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', marginTop: '8px' }}>
                Reset to Default Settings
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div style={{ display: 'flex', gap: '24px', height: '100%', maxWidth: '1200px' }}>
      <div style={{ width: '280px', background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', padding: '16px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a', marginBottom: '16px', padding: '0 8px' }}>Settings</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {settingSections.map((section) => (
            <button key={section.id} onClick={() => setActiveSection(section.id)} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', borderRadius: '8px', border: 'none', background: activeSection === section.id ? '#eff6ff' : 'transparent', color: activeSection === section.id ? '#2563eb' : '#64748b', cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s' }}>
              <section.icon size={18} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>{section.title}</div>
                <div style={{ fontSize: '12px', opacity: 0.7 }}>{section.description}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', padding: '24px', minHeight: '400px' }}>
          {renderSection()}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px' }}>
          {hasChanges && <span style={{ fontSize: '14px', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '6px' }}><RefreshCw size={16} /> Unsaved changes</span>}
          <div style={{ marginLeft: 'auto' }}>
            <button onClick={handleSave} disabled={saved} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px', borderRadius: '8px', border: 'none', background: saved ? '#10b981' : '#2563eb', color: '#ffffff', fontSize: '14px', fontWeight: 500, cursor: saved ? 'default' : 'pointer' }}>
              {saved ? <Check size={18} /> : <Save size={18} />}
              {saved ? 'Saved!' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
