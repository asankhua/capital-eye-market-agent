import React, { useState, useRef, useEffect } from 'react';
import { Bell, User, TrendingUp, Settings } from 'lucide-react';

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
  type: 'alert' | 'info' | 'success';
}

const MOCK_NOTIFICATIONS: Notification[] = [];

export const Header: React.FC<{ onSettingsClick?: () => void }> = ({ onSettingsClick }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(MOCK_NOTIFICATIONS);
  const notifRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (userRef.current && !userRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const getNotifColor = (type: string) => {
    switch (type) {
      case 'alert': return '#f59e0b';
      case 'success': return '#10b981';
      default: return '#3b82f6';
    }
  };
  return (
    <header style={{
      height: '60px',
      background: '#0f172a',
      borderBottom: '1px solid #1e293b',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <TrendingUp size={20} color="white" />
        </div>
        <div>
          <h1 style={{ 
            fontSize: '20px', 
            fontWeight: 700, 
            color: '#ffffff',
            letterSpacing: '-0.5px'
          }}>
            Capital Eye
          </h1>
          <p style={{ 
            fontSize: '11px', 
            color: 'rgba(255,255,255,0.7)',
            letterSpacing: '0.3px'
          }}>
            Intelligent Market Analysis
          </p>
        </div>
      </div>

      {/* Right Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Notifications Dropdown */}
        <div ref={notifRef} style={{ position: 'relative' }}>
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            style={{
              padding: '8px',
              borderRadius: '8px',
              border: 'none',
              background: 'transparent',
              color: 'rgba(255,255,255,0.7)',
              cursor: 'pointer',
              position: 'relative',
            }}
          >
            <Bell size={20} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute',
                top: '4px',
                right: '4px',
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#ef4444',
              }} />
            )}
          </button>
          
          {showNotifications && (
            <div style={{
              position: 'absolute',
              top: '45px',
              right: '0',
              width: '360px',
              background: '#ffffff',
              borderRadius: '12px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
              border: '1px solid #e2e8f0',
              zIndex: 200,
              overflow: 'hidden',
            }}>
              <div style={{
                padding: '16px',
                borderBottom: '1px solid #e2e8f0',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a' }}>
                  Notifications
                </h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={markAllAsRead}
                    style={{
                      fontSize: '12px',
                      color: '#3b82f6',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    Mark all read
                  </button>
                  <button
                    onClick={clearNotifications}
                    style={{
                      fontSize: '12px',
                      color: '#ef4444',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    Clear
                  </button>
                </div>
              </div>
              <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                {notifications.length === 0 ? (
                  <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
                    No notifications yet
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      onClick={() => markAsRead(notif.id)}
                      style={{
                        padding: '12px 16px',
                        borderBottom: '1px solid #f1f5f9',
                        cursor: 'pointer',
                        background: notif.read ? '#ffffff' : '#eff6ff',
                        display: 'flex',
                        gap: '12px',
                        alignItems: 'flex-start',
                      }}
                    >
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: getNotifColor(notif.type),
                        marginTop: '6px',
                        flexShrink: 0,
                      }} />
                      <div style={{ flex: 1 }}>
                        <p style={{ fontSize: '14px', fontWeight: 500, color: '#0f172a' }}>
                          {notif.title}
                        </p>
                        <p style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                          {notif.message}
                        </p>
                        <p style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>
                          {notif.time}
                        </p>
                      </div>
                      {!notif.read && (
                        <div style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          background: '#3b82f6',
                          flexShrink: 0,
                        }} />
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Menu Dropdown */}
        <div ref={userRef} style={{ position: 'relative' }}>
          <button 
            onClick={() => setShowUserMenu(!showUserMenu)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 12px',
              borderRadius: '8px',
              border: 'none',
              background: 'rgba(255,255,255,0.1)',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            <User size={18} />
            <span>Guest</span>
          </button>
          
          {showUserMenu && (
            <div style={{
              position: 'absolute',
              top: '45px',
              right: '0',
              width: '220px',
              background: '#ffffff',
              borderRadius: '12px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
              border: '1px solid #e2e8f0',
              zIndex: 200,
              overflow: 'hidden',
            }}>
              <div style={{
                padding: '16px',
                borderBottom: '1px solid #e2e8f0',
              }}>
                <p style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>Guest User</p>
                <p style={{ fontSize: '12px', color: '#64748b' }}>Welcome to Capital Eye</p>
              </div>
              <button onClick={() => { onSettingsClick?.(); setShowUserMenu(false); }} style={{
                width: '100%',
                padding: '12px 16px',
                textAlign: 'left',
                border: 'none',
                background: '#ffffff',
                color: '#0f172a',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                fontSize: '14px',
              }}>
                <Settings size={18} />
                Settings
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
