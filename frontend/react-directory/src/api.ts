import axios from 'axios';
import { debugLogger } from './debug-logger';
import type {
  AnalysisResponse,
  AnalyzeStockRequest,
  CompareStocksRequest,
  IntentResponse,
  PortfolioRequest,
  ChatRequest,
  WatchlistItem,
  HistoricalAnalysisResponse,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request/response interceptors for logging
apiClient.interceptors.request.use((config) => {
  (config as unknown as Record<string, unknown>).startTime = Date.now();
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    const config = response.config as unknown as Record<string, unknown>;
    const duration = Date.now() - (config.startTime as number || 0);
    const url = (config.url as string) || 'unknown';
    debugLogger.logApiResponse(url, response.data, duration);
    return response;
  },
  (error) => {
    if (error.config) {
      const config = error.config as unknown as Record<string, unknown>;
      const duration = Date.now() - (config.startTime as number || 0);
      const url = (config.url as string) || 'unknown';
      debugLogger.logApiError(url, error.message, duration);
    }
    return Promise.reject(error);
  }
);

export const api = {
  analyzeStock: async (request: AnalyzeStockRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/analyze_stock', request);
    const response = await apiClient.post<AnalysisResponse>('/analyze_stock', request);
    return response.data;
  },

  compareStocks: async (request: CompareStocksRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/compare_stocks', request);
    const response = await apiClient.post<AnalysisResponse>('/compare_stocks', request);
    return response.data;
  },

  portfolioAnalysis: async (request: PortfolioRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/portfolio_analysis', request);
    const response = await apiClient.post<AnalysisResponse>('/portfolio_analysis', request);
    return response.data;
  },

  chat: async (request: ChatRequest): Promise<AnalysisResponse> => {
    debugLogger.logApiRequest('/chat', request);
    const response = await apiClient.post<AnalysisResponse>('/chat', request);
    return response.data;
  },

  parseIntent: async (request: ChatRequest): Promise<IntentResponse> => {
    debugLogger.logApiRequest('/parse_intent', request);
    const response = await apiClient.post<IntentResponse>('/parse_intent', request);
    return response.data;
  },

  // ── Watchlist API ─────────────────────────────────────────────────
  getWatchlist: async (): Promise<WatchlistItem[]> => {
    debugLogger.logApiRequest('/watchlist', {});
    const response = await apiClient.get<WatchlistItem[]>('/watchlist');
    return response.data;
  },

  addToWatchlist: async (ticker: string, notes: string = ''): Promise<{success: boolean; ticker: string}> => {
    debugLogger.logApiRequest(`/watchlist/${ticker}`, { notes });
    const response = await apiClient.post(`/watchlist/${ticker}`, null, { params: { notes } });
    return response.data;
  },

  // ── Historical Analysis API ──────────────────────────────────────
  getHistoricalAnalysis: async (ticker: string, limit: number = 30): Promise<HistoricalAnalysisResponse> => {
    debugLogger.logApiRequest(`/historical/${ticker}`, { limit });
    const response = await apiClient.get<HistoricalAnalysisResponse>(`/historical/${ticker}`, { params: { limit } });
    return response.data;
  },

  // ── NSE Market Movers API ─────────────────────────────────────────
  getNSEMarketMovers: async (type: string = 'gainers'): Promise<{movers: any[], type: string, count: number, source: string}> => {
    debugLogger.logApiRequest('/nse/market_movers', { type });
    const response = await apiClient.get('/nse/market_movers', { params: { type } });
    return response.data;
  },

  // ── NSE Sector API ───────────────────────────────────────────────
  getNSESectorPerformance: async (): Promise<{sectors: any[], count: number, source: string}> => {
    debugLogger.logApiRequest('/nse/sector_performance', {});
    const response = await apiClient.get('/nse/sector_performance');
    return response.data;
  },
  getNSEMarketOverview: async (): Promise<any> => {
    debugLogger.logApiRequest('/nse/market_overview', {});
    const response = await apiClient.get('/nse/market_overview');
    return response.data;
  },

  // ── Indian Stock News API ──────────────────────────────────────────
  getIndianMarketNews: async (max_results: number = 10): Promise<{news: any[], count: number, source: string}> => {
    debugLogger.logApiRequest('/indian_news/market', { max_results });
    const response = await apiClient.get('/indian_news/market', { params: { max_results } });
    return response.data;
  },

};
