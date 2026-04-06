// Watchlist storage utility using localStorage

import { debugLogger } from './debug-logger';

export interface WatchlistItem {
  symbol: string;
  addedAt: number;
  notes?: string;
}

const STORAGE_KEY = 'market_analyst_watchlist';

class WatchlistStorage {
  private getData(): WatchlistItem[] {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  private setData(items: WatchlistItem[]): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }

  getAll(): WatchlistItem[] {
    return this.getData();
  }

  add(symbol: string, notes?: string): boolean {
    const items = this.getData();
    if (items.some(item => item.symbol === symbol)) {
      debugLogger.logUiEvent('Stock already in watchlist', { symbol });
      return false;
    }
    
    items.push({
      symbol,
      addedAt: Date.now(),
      notes,
    });
    this.setData(items);
    debugLogger.logUiEvent('Added to watchlist', { symbol });
    return true;
  }

  remove(symbol: string): boolean {
    const items = this.getData();
    const filtered = items.filter(item => item.symbol !== symbol);
    if (filtered.length === items.length) return false;
    
    this.setData(filtered);
    debugLogger.logUiEvent('Removed from watchlist', { symbol });
    return true;
  }

  isInWatchlist(symbol: string): boolean {
    return this.getData().some(item => item.symbol === symbol);
  }

  clear(): void {
    this.setData([]);
    debugLogger.logUiEvent('Watchlist cleared');
  }
}

export const watchlistStorage = new WatchlistStorage();
