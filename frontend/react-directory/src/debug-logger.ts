// Debug logging utility for capturing API calls and UI events

export type LogLevel = 'info' | 'warn' | 'error' | 'debug';

export interface LogEntry {
  id: string;
  timestamp: number;
  level: LogLevel;
  type: 'api-request' | 'api-response' | 'api-error' | 'ui-event' | 'state-change' | 'error';
  message: string;
  data?: unknown;
  duration?: number;
}

class DebugLogger {
  private logs: LogEntry[] = [];
  private listeners: Set<(logs: LogEntry[]) => void> = new Set();
  private maxLogs: number = 100;

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  addLog(entry: Omit<LogEntry, 'id' | 'timestamp'>): void {
    const logEntry: LogEntry = {
      ...entry,
      id: this.generateId(),
      timestamp: Date.now(),
    };

    this.logs.unshift(logEntry);
    
    // Keep only last N logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs);
    }

    // Notify listeners
    this.listeners.forEach(listener => listener([...this.logs]));
  }

  logApiRequest(endpoint: string, payload: unknown): void {
    this.addLog({
      level: 'info',
      type: 'api-request',
      message: `→ POST ${endpoint}`,
      data: { endpoint, payload },
    });
  }

  logApiResponse(endpoint: string, response: unknown, duration: number): void {
    this.addLog({
      level: 'info',
      type: 'api-response',
      message: `← ${endpoint} (${duration}ms)`,
      data: { endpoint, response },
      duration,
    });
  }

  logApiError(endpoint: string, error: unknown, duration: number): void {
    this.addLog({
      level: 'error',
      type: 'api-error',
      message: `✗ ${endpoint} failed (${duration}ms)`,
      data: { endpoint, error },
      duration,
    });
  }

  logUiEvent(message: string, data?: unknown): void {
    this.addLog({
      level: 'debug',
      type: 'ui-event',
      message,
      data,
    });
  }

  logStateChange(message: string, data?: unknown): void {
    this.addLog({
      level: 'debug',
      type: 'state-change',
      message,
      data,
    });
  }

  logError(message: string, error: unknown): void {
    this.addLog({
      level: 'error',
      type: 'error',
      message,
      data: { error },
    });
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
    this.listeners.forEach(listener => listener([]));
  }

  subscribe(listener: (logs: LogEntry[]) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

export const debugLogger = new DebugLogger();
