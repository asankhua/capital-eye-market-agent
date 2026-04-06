import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bug, X, Trash2, ChevronDown, ChevronUp, Clock, ArrowRight, ArrowLeft, AlertCircle } from 'lucide-react';
import { debugLogger, type LogEntry, type LogLevel } from '../debug-logger';

const LOG_LEVEL_COLORS: Record<LogLevel, string> = {
  info: 'var(--accent-color)',
  warn: 'var(--warning)',
  error: 'var(--danger)',
  debug: '#888',
};

const LOG_TYPE_ICONS: Record<LogEntry['type'], React.ReactNode> = {
  'api-request': <ArrowRight size={14} />,
  'api-response': <ArrowLeft size={14} />,
  'api-error': <AlertCircle size={14} />,
  'ui-event': <Clock size={14} />,
  'state-change': <ChevronDown size={14} />,
  'error': <AlertCircle size={14} />,
};

const LOG_TYPE_LABELS: Record<LogEntry['type'], string> = {
  'api-request': 'API →',
  'api-response': 'API ←',
  'api-error': 'API ✗',
  'ui-event': 'UI',
  'state-change': 'State',
  'error': 'Error',
};

interface DebugPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({ isOpen, onToggle }) => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [expandedLog, setExpandedLog] = useState<string | null>(null);
  const [filter, setFilter] = useState<LogEntry['type'] | 'all'>('all');
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const unsubscribe = debugLogger.subscribe((newLogs) => {
      setLogs(newLogs);
    });
    return unsubscribe;
  }, []);

  const filteredLogs = filter === 'all' 
    ? logs 
    : logs.filter(log => log.type === filter);

  const formatTimestamp = (ts: number): string => {
    const date = new Date(ts);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      fractionalSecondDigits: 3,
    });
  };

  const formatData = (data: unknown): string => {
    try {
      return JSON.stringify(data, null, 2);
    } catch {
      return String(data);
    }
  };

  if (!isOpen) {
    return (
      <motion.button
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.05 }}
        onClick={() => {
            debugLogger.logUiEvent('Debug panel opened');
            onToggle();
          }}
        style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: 'var(--accent-color)',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          zIndex: 1000,
        }}
      >
        <Bug size={24} />
        {logs.length > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              width: '20px',
              height: '20px',
              borderRadius: '50%',
              background: 'var(--danger)',
              fontSize: '12px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {logs.length > 99 ? '99+' : logs.length}
          </span>
        )}
      </motion.button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        width: '500px',
        maxHeight: '60vh',
        background: 'var(--bg-surface)',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          borderBottom: '1px solid var(--border-color)',
          background: 'rgba(0,0,0,0.2)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Bug size={18} color="var(--accent-color)" />
          <span style={{ fontWeight: 600, fontSize: '14px' }}>Debug Logs</span>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)', marginLeft: '8px' }}>
            {filteredLogs.length} entries
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => {
              debugLogger.clearLogs();
              debugLogger.logUiEvent('Logs cleared');
            }}
            style={{
              padding: '6px',
              borderRadius: '6px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
            }}
            title="Clear logs"
          >
            <Trash2 size={16} />
          </button>
          <button
            onClick={onToggle}
            style={{
              padding: '6px',
              borderRadius: '6px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              color: 'var(--text-secondary)',
            }}
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div
        style={{
          display: 'flex',
          gap: '4px',
          padding: '8px 12px',
          borderBottom: '1px solid var(--border-color)',
          overflowX: 'auto',
        }}
      >
        {(['all', 'api-request', 'api-response', 'api-error', 'ui-event', 'error'] as const).map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            style={{
              padding: '4px 10px',
              borderRadius: '12px',
              border: 'none',
              fontSize: '12px',
              cursor: 'pointer',
              background: filter === type ? 'var(--accent-color)' : 'rgba(255,255,255,0.05)',
              color: filter === type ? '#fff' : 'var(--text-secondary)',
              whiteSpace: 'nowrap',
            }}
          >
            {type === 'all' ? 'All' : LOG_TYPE_LABELS[type as LogEntry['type']]}
          </button>
        ))}
      </div>

      {/* Log List */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '8px',
          fontSize: '12px',
          fontFamily: 'monospace',
        }}
      >
        {filteredLogs.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '40px',
              color: 'var(--text-secondary)',
            }}
          >
            No logs yet. Make an API call to see debug info.
          </div>
        ) : (
          filteredLogs.map((log) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              style={{
                marginBottom: '4px',
                borderRadius: '8px',
                background: expandedLog === log.id ? 'rgba(255,255,255,0.05)' : 'transparent',
                border: '1px solid transparent',
                borderColor: expandedLog === log.id ? 'var(--border-color)' : 'transparent',
              }}
            >
              <div
                onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 10px',
                  cursor: 'pointer',
                  borderRadius: '8px',
                  userSelect: 'none',
                }}
              >
                <span style={{ color: LOG_LEVEL_COLORS[log.level] }}>
                  {LOG_TYPE_ICONS[log.type]}
                </span>
                <span style={{ color: 'var(--text-secondary)', fontSize: '11px', minWidth: '70px' }}>
                  {formatTimestamp(log.timestamp)}
                </span>
                <span
                  style={{
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontSize: '10px',
                    background: 'rgba(255,255,255,0.05)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  {LOG_TYPE_LABELS[log.type]}
                </span>
                <span
                  style={{
                    flex: 1,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    color: log.level === 'error' ? 'var(--danger)' : 'var(--text-primary)',
                  }}
                >
                  {log.message}
                </span>
                {log.duration && (
                  <span style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
                    {log.duration}ms
                  </span>
                )}
                {expandedLog === log.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </div>

              <AnimatePresence>
                {expandedLog === log.id && log.data !== undefined && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    style={{
                      overflow: 'hidden',
                    }}
                  >
                    <pre
                      style={{
                        margin: '0 10px 10px',
                        padding: '10px',
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '6px',
                        fontSize: '11px',
                        overflow: 'auto',
                        maxHeight: '200px',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {formatData(log.data)}
                    </pre>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </motion.div>
  );
};
